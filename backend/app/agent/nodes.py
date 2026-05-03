import json
import os
from functools import lru_cache
from typing import Literal

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt

from ..core.config import settings
from ..core.logger import get_logger
from ..session import WealthAdvisorState
from .tools import ALL_TOOLS

logger = get_logger("wealth_advisor.agent")

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "prompts.json")


@lru_cache(maxsize=1)
def load_system_prompt() -> str:
    with open(PROMPTS_PATH) as f:
        return json.load(f)["system_prompt"]


llm = ChatOllama(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0,
)
llm_with_tools = llm.bind_tools(ALL_TOOLS)


def agent_node(state: WealthAdvisorState) -> dict:
    messages = state.messages
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=load_system_prompt())] + list(messages)

    logger.info("Invoking LLM — %d messages in context", len(messages))
    response: AIMessage = llm_with_tools.invoke(messages)

    tool_names = [tc["name"] for tc in response.tool_calls] if response.tool_calls else []
    if tool_names:
        logger.info("LLM selected tools: %s", tool_names)
    else:
        logger.info("LLM produced a final reply (no tool calls)")

    return {"messages": [response]}


def human_approval_node(state: WealthAdvisorState) -> dict:
    last_msg = state.messages[-1]
    tool_calls = last_msg.tool_calls
    tool_names = [tc["name"] for tc in tool_calls]

    tool_call_list = [
        {"name": tc["name"], "args": tc["args"], "id": tc["id"]}
        for tc in tool_calls
    ]

    logger.info("Awaiting user approval — tools=%s", tool_names)
    decision: dict = interrupt({"type": "tool_approval", "tool_calls": tool_call_list})

    if decision.get("approved", False):
        logger.info("Tools approved — %s", tool_names)
        return {"messages": list(state.messages)}

    logger.info("Tools rejected — %s", tool_names)
    rejection_messages: list[BaseMessage] = [
        ToolMessage(
            content="User declined to run this calculation.",
            tool_call_id=tc["id"],
            name=tc["name"],
        )
        for tc in tool_calls
    ]
    return {"messages": rejection_messages}


def route_after_agent(state: WealthAdvisorState) -> Literal["human_approval", "tools", "__end__"]:
    last_msg = state.messages[-1]
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return "__end__"
    tool_names = [tc["name"] for tc in last_msg.tool_calls]
    if tool_names == ["ask_human"]:
        return "tools"
    return "human_approval"


def route_after_approval(state: WealthAdvisorState) -> Literal["tools", "agent"]:
    last_msg = state.messages[-1]
    if isinstance(last_msg, ToolMessage) and last_msg.content == "User declined to run this calculation.":
        return "agent"
    return "tools"
