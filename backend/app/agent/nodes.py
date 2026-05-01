import json
import os
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt

from ..core.config import settings
from ..core.logger import get_logger
from .state import WealthAdvisorState
from .tools import ALL_TOOLS

logger = get_logger("wealth_advisor.agent")

_PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "prompts.json")


@lru_cache(maxsize=1)
def _load_system_prompt() -> str:
    """Cached — reads disk once per process lifetime."""
    with open(_PROMPTS_PATH) as f:
        return json.load(f)["system_prompt"]


# Build the LLM and bind tools once at import time rather than on every agent invocation.
_llm = ChatOllama(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0,
)
_llm_with_tools = _llm.bind_tools(ALL_TOOLS)


class AgentNodeOutput(BaseModel):
    messages: list[BaseMessage]


class HumanApprovalOutput(BaseModel):
    messages: list[BaseMessage]


def agent_node(state: WealthAdvisorState) -> AgentNodeOutput:
    """Invoke the LLM with tools bound. The model decides which tools to call."""
    messages = state.messages
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=_load_system_prompt())] + list(messages)

    logger.info("Invoking LLM — %d messages in context", len(messages))
    response: AIMessage = _llm_with_tools.invoke(messages)

    tool_names = [tc["name"] for tc in response.tool_calls] if response.tool_calls else []
    if tool_names:
        logger.info("LLM selected tools: %s", tool_names)
    else:
        logger.info("LLM produced a final reply (no tool calls)")

    return AgentNodeOutput(messages=[response])


def human_approval_node(state: WealthAdvisorState) -> HumanApprovalOutput:
    """Interrupt before executing non-ask_human tools, presenting them for user approval."""
    last_message = state.messages[-1]
    tool_calls = last_message.tool_calls
    tool_names = [tc["name"] for tc in tool_calls]

    serialised_calls = [
        {"name": tc["name"], "args": tc["args"], "id": tc["id"]}
        for tc in tool_calls
    ]

    logger.info("Awaiting user approval — tools=%s", tool_names)
    decision: dict = interrupt({"type": "tool_approval", "tool_calls": serialised_calls})

    if decision.get("approved", False):
        logger.info("Tools approved — %s", tool_names)
        return HumanApprovalOutput(messages=list(state.messages))

    logger.info("Tools rejected — %s", tool_names)
    rejection_messages: list[BaseMessage] = [
        ToolMessage(
            content="User declined to run this calculation.",
            tool_call_id=tc["id"],
            name=tc["name"],
        )
        for tc in tool_calls
    ]
    return HumanApprovalOutput(messages=rejection_messages)


def route_after_agent(state: WealthAdvisorState) -> Literal["human_approval", "tools", "__end__"]:
    """
    ask_human → tools directly (it calls interrupt() internally).
    Other tools  → human_approval first.
    No tools     → end the turn.
    """
    last = state.messages[-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return "__end__"
    tool_names = [tc["name"] for tc in last.tool_calls]
    if tool_names == ["ask_human"]:
        return "tools"
    return "human_approval"


def route_after_approval(state: WealthAdvisorState) -> Literal["tools", "agent"]:
    """Loop back to agent if the user rejected all tools; otherwise execute them."""
    last = state.messages[-1]
    if isinstance(last, ToolMessage) and last.content == "User declined to run this calculation.":
        return "agent"
    return "tools"
