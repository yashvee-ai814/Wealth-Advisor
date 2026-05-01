from typing import Annotated
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class WealthAdvisorState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []
