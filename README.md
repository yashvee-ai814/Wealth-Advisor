# Wealth Advisor

An AI-powered UK wealth and retirement planning chatbot. Have a natural conversation about your retirement goals, pension pot projections, savings targets, and income planning. The LLM runs entirely on your own Mac via Ollama — no API key or internet required.

## What it does

- **Conversational chat** — ask questions naturally, receive follow-up advice across multiple turns
- **Agentic tool selection** — the AI automatically picks the right financial calculation tool for each question
- **Deterministic math** — all projections use hardcoded financial formulas (compound growth, drawdown, inflation), not AI guesswork
- **Human-in-the-loop** — before any calculation runs, you see the tool and its inputs and can approve or reject
- **Clarification flow** — when the AI needs missing data mid-conversation, it pauses and asks you

## Architecture

Three microservices wired together with Docker Compose:

- **frontend** — React 18 + Vite + Tailwind CSS, served on port 5173
- **backend** — Python FastAPI + LangGraph agent + 8 MCP tools, served on port 8000
- **ollama** — runs natively on your Mac (outside Docker); backend reaches it via `host.docker.internal:11434`

```
Browser → frontend:5173  →  backend:8000  →  Ollama (Mac host):11434
```

### LangGraph agent graph

```
User message
    │
    ▼
agent_node  ──► human_approval_node ──► tools_node ──► agent_node (loop)
    │                                       ▲
    └──► ask_human tool → interrupt() ──────┘
    │
    └──► END (final reply)
```

### MCP tools (all pure Python math — no LLM in calculations)

| Tool | Formula |
|------|---------|
| `calculate_projected_pot` | Future value annuity: `FV = PV*(1+r)^n + PMT*((1+r)^n-1)/r` |
| `calculate_drawdown_income` | `income = pot * drawdown_rate + state_pension` |
| `calculate_monthly_savings_needed` | Rearranged FV annuity for PMT |
| `calculate_shortfall` | `max(0, income_goal - projected_income)` |
| `calculate_readiness_score` | `min(100, projected/goal * 100)` → score + label |
| `calculate_inflation_adjusted_goal` | `FV = goal * (1 + inflation)^years` |
| `get_uk_state_pension_info` | £11,502/yr from age 67 lookup |
| `ask_human` | Triggers `interrupt()` to pause for clarification |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Ollama installed on Mac:
  ```bash
  brew install ollama
  ```
- Model pulled:
  ```bash
  ollama pull gpt-oss:120b-cloud
  ```

## How to run (Docker)

**Step 1:** Start Ollama on your Mac:
```bash
ollama serve
```

**Step 2:** Start the full app:
```bash
docker compose up --build
```

**Step 3:** Open [http://localhost:5173](http://localhost:5173)

---

## Local dev (no Docker)

```bash
# Tab 1 — Ollama
ollama serve

# Tab 2 — Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Tab 3 — Frontend
cd frontend
npm install
npm run dev
```

---

## Project structure

```
Wealth-Advisor/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api/
│       │   ├── advisor.ts        ← legacy single-turn assess endpoint
│       │   └── chat.ts           ← conversational chat + interrupt resume
│       ├── types/
│       │   ├── advisor.ts        ← legacy types
│       │   └── chat.ts           ← ChatMessage, ChatResponse, PendingInterrupt
│       └── components/
│           ├── ChatWindow.jsx    ← scrollable message list
│           ├── ChatInput.jsx     ← textarea + send button
│           ├── MessageBubble.jsx ← user / assistant bubbles
│           ├── ToolCallBadge.jsx ← chip showing which tool was used
│           ├── ToolApprovalCard.jsx ← approve/reject before tool execution
│           ├── ClarificationCard.jsx ← answer agent's mid-flow question
│           ├── AdvisorForm.jsx   ← legacy form (powers /assess)
│           ├── ResultCard.jsx    ← legacy result card
│           └── LoadingSpinner.jsx
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
│       ├── __init__.py
│       ├── main.py           ← FastAPI app + CORS
│       ├── router.py         ← /health, /assess (legacy), /chat
│       ├── models.py         ← legacy Pydantic models for /assess
│       ├── chat_models.py    ← ChatRequest, ChatResponse, PendingInterrupt
│       ├── tools.py          ← 8 MCP tools with Pydantic input/output models
│       ├── agent.py          ← LangGraph StateGraph with HIL interruption
│       ├── llm.py            ← legacy direct LLM call for /assess
│       └── config.py         ← pydantic-settings (OLLAMA_BASE_URL, OLLAMA_MODEL)
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check + active model name |
| POST | `/chat` | Send a message or resume an interrupt |
| DELETE | `/chat/{session_id}` | Clear session (start fresh) |
| POST | `/assess` | Legacy single-turn retirement assessment |

### POST /chat request body

```json
{
  "session_id": "session-abc123",
  "message": "I'm 40, earn £70k, want to retire at 65 with £40k/yr",
  "resume_input": null
}
```

To resume after a tool-approval interrupt:
```json
{ "session_id": "session-abc123", "resume_input": { "approved": true } }
```

To resume after a clarification interrupt:
```json
{ "session_id": "session-abc123", "resume_input": { "answer": "My pension pot is £30,000" } }
```

---

## Tech stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Web framework | FastAPI |
| Agent orchestration | LangGraph |
| LLM integration | langchain-openai (OpenAI-compatible Ollama endpoint) |
| Validation | Pydantic v2 everywhere (tools, nodes, state, API) |
| Package manager | uv |
| Frontend | React 18 + Vite 5 + Tailwind CSS v3 |
| LLM runtime | Ollama (local, no API key) |
| Containers | Docker + Docker Compose |
