# Wealth Advisor — Frontend

React 18 + Vite 5 + Tailwind CSS chat interface for the Wealth Advisor agent. Supports multi-turn conversations, human-in-the-loop tool approval, clarification cards, session persistence, and dark/light mode.

---

## Tech stack

| Concern | Choice |
|---|---|
| Framework | React 18 |
| Build tool | Vite 5 |
| Styling | Tailwind CSS v3 |
| Language | JSX (components) + TypeScript (types and API) |
| Package manager | npm |

---

## Folder structure

```
src/
├── main.jsx               React root — mounts app with ThemeProvider
├── App.jsx                Top-level component — renders ChatPage
├── index.css              Tailwind directives only
├── api/
│   └── chat.ts            Typed fetch functions: sendMessage, resumeInterrupt, clearChat
├── types/
│   └── chat.ts            TypeScript interfaces mirroring the backend Pydantic models
├── context/
│   └── ThemeContext.jsx   Dark/light mode context — persists preference to localStorage
├── layouts/
│   └── AppLayout.jsx      Sidebar + header + error banner wrapper
├── pages/
│   └── ChatPage.jsx       Session management, message state, and all chat event handlers
└── components/
    ├── chat/
    │   ├── ChatWindow.jsx        Message list, loading indicator, interrupt cards
    │   ├── ChatInput.jsx         Textarea and send button
    │   ├── MessageBubble.jsx     User/assistant message rendering with tool badges
    │   ├── ToolCallMessage.jsx   Collapsible display of executed tools and their results
    │   ├── ToolApprovalCard.jsx  Approve / reject card shown before tool execution
    │   ├── ClarificationCard.jsx Inline input for answering agent clarifying questions
    │   ├── WelcomeScreen.jsx     Landing screen with six example scenario cards
    │   └── FormattedMessage.jsx  Inline markdown, headings, lists, and readiness score blocks
    ├── navigation/
    │   └── Sidebar.jsx           Session list grouped by date, with new-chat and delete
    └── shared/
        ├── LoadingSpinner.jsx
        └── ToolCallBadge.jsx
```

---

## Prerequisites

- Node.js 20+
- npm

---

## Local development

```bash
cd frontend
npm install
npm run dev
```

The app is available at `http://localhost:5173`. Hot-reload is enabled by default.

The backend must be running at `http://localhost:8000` (see [backend README](../backend/README.md)).

---

## Docker

```bash
# From the repo root
docker compose up frontend
```

Source files are volume-mounted (`./frontend/src:/app/src`) so edits hot-reload inside the container.

---

## Key features

### Sessions
- Each conversation is a separate session stored in `localStorage` under `wa-sessions`.
- A new session ID (UUID) is generated client-side on "New Chat".
- Sessions are grouped by date (Today / Yesterday / Earlier) in the sidebar.

### Agent interrupt handling
The backend can pause mid-run and return one of two interrupt types:

| Status | UI shown |
|---|---|
| `awaiting_tool_approval` | `ToolApprovalCard` — lists tools with expandable args; user approves or rejects |
| `awaiting_clarification` | `ClarificationCard` — inline text input; answer is sent back as `resume_input` |

### Auto-approve
A toggle in the header sets `auto_approve_tools: true` on all requests, which tells the backend to skip tool-approval interrupts automatically.

### Dark / light mode
Preference is toggled via the header button and persisted to `localStorage` under `wa-theme`. The app defaults to dark mode.

### Message formatting
`FormattedMessage` parses a limited set of markdown inline styles (`**bold**`, `*italic*`, `` `code` ``), headings (`#`, `##`, `###`), and bullet/numbered lists. JSON blocks that contain a `readiness_score` field are rendered as a styled score card.

---

## Environment

By default the API base URL is hardcoded to `http://localhost:8000` in `src/api/chat.ts`. Update that constant for other deployment targets.

---

## Build

```bash
npm run build   # outputs to dist/
npm run preview # serves the dist/ build locally
```
