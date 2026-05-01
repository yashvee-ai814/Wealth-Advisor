from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command

from .models import ChatRequest, ChatResponse, ToolCallInfo, PendingInterrupt
from .config import settings
from .agent import graph

router = APIRouter()

# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all previous", "forget your instructions",
    "pretend you are", "act as if you are", "you are now a", "jailbreak",
    "override your", "disregard your", "system prompt", "<script>",
    "select * from", "drop table", "'; drop", "ignore your system",
    "new instructions:", "[system]", "###instruction",
]

_BLOCKED_DOMAINS = [
    "how to hack", "make a bomb", "build a weapon", "illegal drugs",
    "suicide method", "self-harm method", "commit violence", "terrorism",
    "child abuse", "exploit vulnerability",
]

_WEALTH_HINTS = [
    "pension", "retirement", "saving", "invest", "income", "salary", "wealth",
    "pot", "fund", "isa", "tax", "drawdown", "contribution", "annuity",
    "financial", "money", "£", "gbp", "budget", "mortgage", "insurance",
    "state pension", "advisor", "plan", "goal", "age", "year", "month",
    "hi", "hello", "thanks", "thank", "help", "what", "how", "when",
    "can you", "could you", "would you", "please", "i am", "i'm", "my",
]


def _guardrail(message: str) -> tuple[bool, str]:
    lower = message.lower()
    for p in _INJECTION_PATTERNS:
        if p in lower:
            return False, "I can only assist with UK wealth planning and retirement questions. The message you sent appears to contain instructions that I cannot follow."
    for p in _BLOCKED_DOMAINS:
        if p in lower:
            return False, "I'm a UK wealth advisor and can only help with financial planning, retirement, and savings questions."
    has_hint = any(h in lower for h in _WEALTH_HINTS)
    if not has_hint and len(message.split()) > 8:
        return False, "I specialise in UK wealth planning, retirement, pensions, and savings. Could you rephrase your question in that context?"
    return True, ""


def _check_ai_output(reply: str) -> bool:
    lower = reply.lower()
    for p in ["ignore previous", "new instructions:", "[system]", "<script>"]:
        if p in lower:
            return False
    return True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/health")
async def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    config = {"configurable": {"thread_id": req.session_id}}

    if req.resume_input is not None:
        result = graph.invoke(Command(resume=req.resume_input), config=config)
    elif req.message:
        ok, reason = _guardrail(req.message)
        if not ok:
            return ChatResponse(
                session_id=req.session_id,
                reply=reason,
                status="complete",
                tool_calls_used=[],
            )
        result = graph.invoke(
            {"messages": [HumanMessage(content=req.message)]},
            config=config,
        )
    else:
        raise HTTPException(status_code=400, detail="Either message or resume_input must be provided")

    # Auto-approve loop: keep resuming tool-approval interrupts without human input
    if req.auto_approve_tools:
        while True:
            state = graph.get_state(config)
            if not state.next:
                break
            interrupt_data = state.tasks[0].interrupts[0].value if state.tasks else {}
            if isinstance(interrupt_data, dict) and interrupt_data.get("type") == "tool_approval":
                result = graph.invoke(Command(resume={"approved": True}), config=config)
            else:
                break

    state = graph.get_state(config)
    is_interrupted = bool(state.next)

    # Extract tool calls used in this turn
    tool_calls_used: list[ToolCallInfo] = []
    messages = result.get("messages", [])
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_used.append(ToolCallInfo(name=tc["name"], args=tc["args"]))
        if isinstance(msg, ToolMessage) and tool_calls_used:
            for tci in tool_calls_used:
                if tci.result is None and tci.name != "ask_human":
                    tci.result = str(msg.content)[:500]

    # Determine status and pending interrupt payload
    status = "complete"
    pending_interrupt: PendingInterrupt | None = None

    if is_interrupted:
        interrupt_data = state.tasks[0].interrupts[0].value if state.tasks else {}

        if isinstance(interrupt_data, dict) and interrupt_data.get("type") == "tool_approval":
            status = "awaiting_tool_approval"
            pending_interrupt = PendingInterrupt(
                type="tool_approval",
                tool_calls=[
                    ToolCallInfo(name=tc["name"], args=tc["args"])
                    for tc in interrupt_data.get("tool_calls", [])
                ],
            )
        else:
            question = interrupt_data if isinstance(interrupt_data, str) else str(interrupt_data)
            status = "awaiting_clarification"
            pending_interrupt = PendingInterrupt(type="clarification", question=question)

    # Get the last assistant reply
    reply = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            reply = msg.content
            break

    if not reply and status == "complete":
        reply = "I've completed the analysis. Let me know if you have any questions."

    if reply and not _check_ai_output(reply):
        reply = "I apologise, but I couldn't generate a safe response for that request. Please try rephrasing your question."

    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        status=status,
        pending_interrupt=pending_interrupt,
        tool_calls_used=tool_calls_used,
    )


@router.delete("/chat/{session_id}")
async def clear_chat(session_id: str):
    """Clear conversation history for a session (start fresh)."""
    # MemorySaver doesn't expose delete; the frontend generates a new session_id for fresh chats.
    return {"status": "ok", "session_id": session_id}
