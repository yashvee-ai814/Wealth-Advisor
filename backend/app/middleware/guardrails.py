"""
Input and output safety checks for the wealth advisor API.

All checks are pure functions — no FastAPI dependencies — so they can be
unit-tested independently and called from any route handler.
"""

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

# Loose allowlist: if none of these appear in a long message, reject it.
_WEALTH_HINTS = [
    "pension", "retirement", "saving", "invest", "income", "salary", "wealth",
    "pot", "fund", "isa", "tax", "drawdown", "contribution", "annuity",
    "financial", "money", "£", "gbp", "budget", "mortgage", "insurance",
    "state pension", "advisor", "plan", "goal", "age", "year", "month",
    "hi", "hello", "thanks", "thank", "help", "what", "how", "when",
    "can you", "could you", "would you", "please", "i am", "i'm", "my",
]

_OUTPUT_INJECTION_PATTERNS = [
    "ignore previous", "new instructions:", "[system]", "<script>",
]


def check_input(message: str) -> tuple[bool, str]:
    """
    Validate a user message before it is sent to the agent.

    Returns (True, "") when the message is safe.
    Returns (False, reason) when it should be blocked.
    """
    lower = message.lower()

    for pattern in _INJECTION_PATTERNS:
        if pattern in lower:
            return (
                False,
                "I can only assist with UK wealth planning and retirement questions. "
                "The message you sent appears to contain instructions that I cannot follow.",
            )

    for pattern in _BLOCKED_DOMAINS:
        if pattern in lower:
            return (
                False,
                "I'm a UK wealth advisor and can only help with financial planning, "
                "retirement, and savings questions.",
            )

    has_wealth_hint = any(hint in lower for hint in _WEALTH_HINTS)
    if not has_wealth_hint and len(message.split()) > 8:
        return (
            False,
            "I specialise in UK wealth planning, retirement, pensions, and savings. "
            "Could you rephrase your question in that context?",
        )

    return True, ""


def check_output(reply: str) -> bool:
    """
    Scan an AI reply for injection artefacts before returning it to the client.

    Returns True when the reply is safe to send, False when it should be suppressed.
    """
    lower = reply.lower()
    return not any(pattern in lower for pattern in _OUTPUT_INJECTION_PATTERNS)
