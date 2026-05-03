# Wealth Advisor — Frontend

React 18 + Vite 5 + Tailwind CSS chat interface for the Wealth Advisor agent. Supports multi-turn conversations, human-in-the-loop tool approval, clarification cards, session persistence, and dark/light mode.

---

## Features

- **Sessions** — multiple conversations stored in `localStorage` under `wa-sessions`, grouped by date in the sidebar
- **Tool approval** — before any calculation runs, a card shows the tool name and inputs; you approve or reject
- **Clarification** — when the agent needs missing information, an inline card lets you answer; the reply resumes the workflow
- **Auto-approve toggle** — skip the approval step and let all tools run automatically
- **Dark / light mode** — toggled via the header, persisted in `localStorage` under `wa-theme`
- **Markdown rendering** — bold, italics, code, headings, lists, and readiness score blocks

---

## Component structure

```
src/
├── main.jsx                        React root entry point
├── App.jsx                         Top-level component, ThemeContext provider
├── index.css                       Tailwind directives and custom utilities
├── api/
│   └── chat.ts                     sendMessage, resumeInterrupt, clearChat
├── types/
│   └── chat.ts                     TypeScript interfaces mirroring Pydantic models
├── context/
│   └── ThemeContext.jsx            Dark/light mode state and toggle
├── layouts/
│   └── AppLayout.jsx               Sidebar + header + error banner wrapper
├── pages/
│   └── ChatPage.jsx                Session management, message state, and chat event handlers
└── components/
    ├── chat/
    │   ├── ChatWindow.jsx          Scrollable message list with loading indicator and interrupt cards
    │   ├── ChatInput.jsx           Textarea and send button
    │   ├── MessageBubble.jsx       User/assistant message with tool badges
    │   ├── FormattedMessage.jsx    Inline markdown, headings, lists, and readiness score blocks
    │   ├── ToolCallMessage.jsx     Collapsible display of executed tool calls and results
    │   ├── ToolApprovalCard.jsx    Approve/reject card shown before tool execution
    │   ├── ClarificationCard.jsx   Inline input for answering agent clarifying questions
    │   └── WelcomeScreen.jsx       Landing screen with six example scenario cards
    ├── navigation/
    │   └── Sidebar.jsx             Session list grouped by date, new chat and delete actions
    └── shared/
        ├── LoadingSpinner.jsx      Animated loading indicator
        └── ToolCallBadge.jsx       Small inline badge showing a tool name
```

---

## Agent interrupt handling

The backend pauses mid-run and returns one of two interrupt types:

| Status | UI component | Action |
|---|---|---|
| `awaiting_tool_approval` | `ToolApprovalCard` | Shows tool names and args; user approves or rejects |
| `awaiting_clarification` | `ClarificationCard` | Inline text input; answer sent back as `resume_input` |

---

## Prerequisites

- Node.js 20+
- Backend running at `http://localhost:8000` — see [backend/README.md](../backend/README.md)

---

## Local development

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:5173`. Hot-reload is enabled by default.

---

## Docker

```bash
# From the repo root
docker compose up frontend
```

Source files are volume-mounted (`./frontend/src:/app/src`) so edits hot-reload inside the container.

---

## Build

```bash
npm run build   # outputs to dist/
npm run preview # serves dist/ locally for inspection
```

---

## API base URL

Hardcoded to `http://localhost:8000` in `src/api/chat.ts`. Update that constant for other deployment targets.
