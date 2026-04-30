import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.types import interrupt

from ..llm import build_llm
from .tools import ALL_TOOLS

# ---------------------------------------------------------------------------
# Load system prompt from data/prompts.json
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data"

def _load_system_prompt() -> str:
    with open(_DATA_DIR / "prompts.json") as f:
        return json.load(f)["system_prompt"]

SYSTEM_PROMPT = _load_system_prompt()


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class WealthAdvisorState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []


# ---------------------------------------------------------------------------
# Node I/O models
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
# Nodes
# ---------------------------------------------------------------------------

def agent_node(state: WealthAdvisorState) -> AgentNodeOutput:
    """Invoke the LLM with all tools bound. The LLM decides which tools to call."""
    llm = build_llm().bind_tools(ALL_TOOLS)

    messages = state.messages
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

    response: AIMessage = llm.invoke(messages)
    return AgentNodeOutput(messages=[response])


def human_approval_node(state: WealthAdvisorState) -> HumanApprovalOutput:
    """
    Interrupt before executing non-ask_human tool calls.
    Presents pending tool calls to the user for approval or rejection.
    """
    last_message = state.messages[-1]
    tool_calls = last_message.tool_calls

    decision: dict = interrupt({
        "type": "tool_approval",
        "tool_calls": [
            {"name": tc["name"], "args": tc["args"], "id": tc["id"]}
            for tc in tool_calls
        ],
    })

    if decision.get("approved", False):
        return HumanApprovalOutput(messages=list(state.messages))

    # User rejected — inject ToolMessages so the agent can respond gracefully
    return HumanApprovalOutput(messages=[
        ToolMessage(
            content="User declined to run this calculation.",
            tool_call_id=tc["id"],
            name=tc["name"],
        )
        for tc in tool_calls
    ])


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_after_agent(state: WealthAdvisorState) -> Literal["human_approval", "tools", "__end__"]:
    last = state.messages[-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return "__end__"
    tool_names = [tc["name"] for tc in last.tool_calls]
    if tool_names == ["ask_human"]:
        return "tools"
    return "human_approval"


def route_after_approval(state: WealthAdvisorState) -> Literal["tools", "agent"]:
    last = state.messages[-1]
    if isinstance(last, ToolMessage) and last.content == "User declined to run this calculation.":
        return "agent"
    return "tools"
