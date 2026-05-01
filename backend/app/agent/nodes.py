import json
import os
from typing import Literal

from pydantic import BaseModel
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt

from ..llm import build_llm
from .state import WealthAdvisorState
from .tools import ALL_TOOLS


def _load_system_prompt() -> str:
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "prompts.json")
    with open(data_path) as f:
        return json.load(f)["system_prompt"]


class AgentNodeOutput(BaseModel):
    messages: list[BaseMessage]


class HumanApprovalOutput(BaseModel):
    messages: list[BaseMessage]


def agent_node(state: WealthAdvisorState) -> AgentNodeOutput:
    """Invoke the LLM with all tools bound. The LLM decides which tools to call."""
    llm = build_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    messages = state.messages
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=_load_system_prompt())] + list(messages)

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


def route_after_agent(state: WealthAdvisorState) -> Literal["human_approval", "tools", "__end__"]:
    """
    Decide what to do after the agent responds:
    - ask_human tool: go directly to tools (ask_human calls interrupt() internally)
    - other tools: go to human_approval first
    - no tools: end the turn
    """
    last = state.messages[-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return "__end__"

    tool_names = [tc["name"] for tc in last.tool_calls]
    if tool_names == ["ask_human"]:
        return "tools"
    return "human_approval"


def route_after_approval(state: WealthAdvisorState) -> Literal["tools", "agent"]:
    """After human_approval_node: if tools were rejected, loop back to agent; else run tools."""
    last = state.messages[-1]
    if isinstance(last, ToolMessage) and last.content == "User declined to run this calculation.":
        return "agent"
    return "tools"
