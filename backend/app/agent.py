from typing import Annotated, Literal
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from .config import settings
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """You are a knowledgeable and friendly UK wealth advisor chatbot. You help users with:
- Retirement planning and readiness assessment
- Pension pot projections and contribution advice
- Retirement income goals and drawdown strategies
- UK state pension eligibility and amounts
- Understanding shortfalls and how to close them
- ISAs, investment products, and savings strategies

CRITICAL RULES:
1. NEVER perform mathematical calculations yourself. Always use the provided tools for any numeric calculation.
2. If you are missing any data needed to run a calculation, call the ask_human tool to request it — never guess or assume values.
3. Always use get_uk_state_pension_info to get state pension details before including it in income projections.
4. For full retirement assessments, run tools in this order:
   a. get_uk_state_pension_info
   b. calculate_projected_pot
   c. calculate_drawdown_income (using projected pot + state pension)
   d. calculate_shortfall
   e. calculate_readiness_score
5. Use calculate_inflation_adjusted_goal when the user states an income goal in today's money.
6. Be conversational, warm, and explain results in plain English after receiving tool outputs.
7. Always include this disclaimer when giving financial projections:
   "This is not financial advice. Projections are estimates based on assumed growth rates. Please consult a qualified financial adviser."
"""


# ---------------------------------------------------------------------------
# Graph State
# ---------------------------------------------------------------------------

class WealthAdvisorState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []


# ---------------------------------------------------------------------------
# Node input/output models
# ---------------------------------------------------------------------------

class AgentNodeInput(BaseModel):
    messages: list[BaseMessage]


class AgentNodeOutput(BaseModel):
    messages: list[BaseMessage]


class HumanApprovalInput(BaseModel):
    messages: list[BaseMessage]


class HumanApprovalOutput(BaseModel):
    messages: list[BaseMessage]


# ---------------------------------------------------------------------------
# LLM setup
# ---------------------------------------------------------------------------

def _build_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def agent_node(state: WealthAdvisorState) -> AgentNodeOutput:
    """Invoke the LLM with all tools bound. The LLM decides which tools to call."""
    llm = _build_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    messages = state.messages
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

    response: AIMessage = llm_with_tools.invoke(messages)
    return AgentNodeOutput(messages=[response])


def human_approval_node(state: WealthAdvisorState) -> HumanApprovalOutput:
    """
    Interrupt the graph before executing non-ask_human tool calls.
    Presents the pending tool calls to the user for approval or rejection.
    """
    last_message = state.messages[-1]
    tool_calls = last_message.tool_calls

    serialised_calls = [
        {"name": tc["name"], "args": tc["args"], "id": tc["id"]}
        for tc in tool_calls
    ]

    decision: dict = interrupt({
        "type": "tool_approval",
        "tool_calls": serialised_calls,
    })

    if decision.get("approved", False):
        return HumanApprovalOutput(messages=list(state.messages))

    # User rejected — inject ToolMessages that report the rejection so the
    # agent can respond gracefully without executing the tools.
    rejection_messages: list[BaseMessage] = []
    for tc in tool_calls:
        rejection_messages.append(
            ToolMessage(
                content="User declined to run this calculation.",
                tool_call_id=tc["id"],
                name=tc["name"],
            )
        )
    return HumanApprovalOutput(messages=rejection_messages)


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_after_agent(state: WealthAdvisorState) -> Literal["human_approval", "tools", "__end__"]:
    """
    Decide what to do after the agent responds:
    - If the agent called ask_human: go directly to tools (ask_human calls interrupt() internally)
    - If the agent called other tools: go to human_approval first
    - Otherwise: end the turn
    """
    last = state.messages[-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return "__end__"

    tool_names = [tc["name"] for tc in last.tool_calls]

    if tool_names == ["ask_human"]:
        return "tools"

    return "human_approval"


def route_after_approval(state: WealthAdvisorState) -> Literal["tools", "agent"]:
    """After human_approval_node: if tools were rejected, go back to agent; else run tools."""
    last = state.messages[-1]
    if isinstance(last, ToolMessage) and last.content == "User declined to run this calculation.":
        return "agent"
    return "tools"


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    builder = StateGraph(WealthAdvisorState)

    builder.add_node("agent", agent_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.set_entry_point("agent")

    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "human_approval": "human_approval",
            "tools": "tools",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "tools": "tools",
            "agent": "agent",
        },
    )

    builder.add_edge("tools", "agent")

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


graph = build_graph()
