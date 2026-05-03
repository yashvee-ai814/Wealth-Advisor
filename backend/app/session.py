from typing import Annotated

from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


class WealthAdvisorState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []


checkpointer = MemorySaver()


def make_config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}
