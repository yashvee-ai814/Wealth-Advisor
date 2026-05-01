from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str | None = None
    resume_input: dict | None = None
    auto_approve_tools: bool = False


class ToolCallInfo(BaseModel):
    name: str
    args: dict
    result: str | None = None


class PendingInterrupt(BaseModel):
    type: Literal["tool_approval", "clarification"]
    tool_calls: list[ToolCallInfo] | None = None
    question: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    status: Literal["complete", "awaiting_tool_approval", "awaiting_clarification"]
    pending_interrupt: PendingInterrupt | None = None
    tool_calls_used: list[ToolCallInfo] = Field(default_factory=list)
