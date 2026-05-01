# Wealth Advisor — Backend

FastAPI + LangGraph backend for the UK wealth advisor chatbot.

## Structure

```
app/
├── main.py          ← FastAPI app + CORS middleware
├── router.py        ← API routes: /health, POST /chat, DELETE /chat/{id}
├── models.py        ← Pydantic models: ChatRequest, ChatResponse, ToolCallInfo, PendingInterrupt
├── config.py        ← pydantic-settings: OLLAMA_BASE_URL, OLLAMA_MODEL
├── llm.py           ← ChatOllama client builder
├── data/
│   └── prompts.json ← system prompt (loaded at runtime by agent_node)
└── agent/
    ├── __init__.py  ← exports compiled graph
    ├── state.py     ← WealthAdvisorState (Annotated messages list)
    ├── tools.py     ← 8 MCP tools + ALL_TOOLS list
    ├── nodes.py     ← agent_node, human_approval_node, route_after_agent, route_after_approval
    └── graph.py     ← StateGraph with MemorySaver checkpointer
```

## Agent graph

```
agent_node
    │
    ├─ ask_human call ──────────────→ tools → agent_node (loop)
    │
    ├─ other tool calls ─→ human_approval_node
    │                           │
    │                           ├─ approved ──→ tools → agent_node (loop)
    │                           └─ rejected ──→ agent_node
    │
    └─ no tools ──→ END
```

## Tools

All 8 tools use deterministic Python math — the LLM never performs calculations itself.

| Tool | What it does |
|------|-------------|
| `calculate_projected_pot` | Future value of pension pot at retirement |
| `calculate_drawdown_income` | Annual income from pot + state pension |
| `calculate_monthly_savings_needed` | Monthly saving required to hit a target pot |
| `calculate_shortfall` | Gap between income goal and projected income |
| `calculate_readiness_score` | Score 0-100 + label (On track / Needs attention / At risk) |
| `calculate_inflation_adjusted_goal` | Income goal adjusted for inflation |
| `get_uk_state_pension_info` | £11,502/yr state pension from age 67 |
| `ask_human` | Pauses graph via `interrupt()` to request missing data |

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns `{"status": "ok", "model": "..."}` |
| POST | `/chat` | Send a message or resume an interrupt |
| DELETE | `/chat/{session_id}` | Clear session (start fresh) |

## Local dev

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gpt-oss:120b-cloud` | Model name to use |
