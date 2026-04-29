# Retirement Readiness Advisor

An AI-powered UK retirement readiness tool. Enter your age, salary, pension pot, contributions, and retirement goal — and receive an AI-generated readiness score, financial projection, and personalised action plan. The LLM runs entirely on your own Mac via Ollama — no API key or internet required.

## Architecture

Three microservices wired together with Docker Compose:

- **frontend** — React 18 + Vite + Tailwind CSS, served on port 5173
- **backend** — Python FastAPI + Pydantic v2, served on port 8000
- **ollama** — runs natively on your Mac (outside Docker); the backend reaches it via `host.docker.internal:11434`

```
Browser → frontend:5173  →  backend:8000  →  Ollama (Mac host):11434
```

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

## How to run

**Step 1:** Start Ollama on your Mac (runs outside Docker):
```bash
ollama serve
```

**Step 2:** Pull the model if not already done:
```bash
ollama pull gpt-oss:120b-cloud
```

**Step 3:** Start the full app with one command:
```bash
docker compose up --build
```

**Step 4:** Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running backend locally without Docker (for development)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

## Running frontend locally without Docker

```bash
cd frontend
npm install
npm run dev
```

---

## Project structure

```
retirement-advisor/
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
│       │   └── advisor.ts
│       ├── types/
│       │   └── advisor.ts
│       └── components/
│           ├── AdvisorForm.jsx
│           ├── ResultCard.jsx
│           └── LoadingSpinner.jsx
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── router.py
│       ├── models.py
│       ├── llm.py
│       └── config.py
```

---

## What I learned

Building this project introduced several real-world concepts:

- **Microservice architecture** — separating concerns into independent services that communicate over HTTP
- **FastAPI** — modern Python web framework with automatic OpenAPI docs and request validation
- **Pydantic v2** — powerful data validation and serialisation for Python
- **uv** — blazing-fast Python package manager that replaces pip/venv/poetry
- **React with JSX** — component-based UI development with hooks and state
- **Ollama local LLM** — running a large language model entirely on your own hardware, no API key needed
- **Docker Compose** — orchestrating multiple services with a single command
- **UK pension domain knowledge** — applying state pension rules, drawdown rates, and inflation assumptions to real financial projections
