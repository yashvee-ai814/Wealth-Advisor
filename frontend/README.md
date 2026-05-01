# Wealth Advisor — Frontend

React 18 + Vite 5 + Tailwind CSS frontend for the UK wealth advisor chatbot.

## Structure

```
src/
├── main.jsx              ← React entry point
├── App.jsx               ← root component: session management, chat state, interrupts
├── index.css             ← @tailwind directives
├── api/
│   └── chat.ts           ← sendMessage, resumeInterrupt, clearChat (typed fetch functions)
├── types/
│   └── chat.ts           ← TypeScript interfaces mirroring backend Pydantic models
├── context/
│   └── ThemeContext.jsx  ← dark/light mode (persisted to localStorage)
└── components/
    ├── chat/             ← UI shell components
    │   ├── ChatWindow.jsx       ← scrollable message list + loading dots
    │   ├── ChatInput.jsx        ← textarea + send button
    │   ├── MessageBubble.jsx    ← user / assistant / clarification bubbles
    │   ├── FormattedMessage.jsx ← markdown renderer (bold, italic, lists, headings)
    │   ├── WelcomeScreen.jsx    ← hero + 6 example scenario cards
    │   ├── Sidebar.jsx          ← session list grouped by date
    │   └── LoadingSpinner.jsx
    └── tools/            ← agent interaction components
        ├── ToolApprovalCard.jsx  ← approve/reject tool calls before execution
        ├── ToolCallMessage.jsx   ← displays executed tools with inputs/results
        ├── ToolCallBadge.jsx     ← small chip showing which tool was used
        └── ClarificationCard.jsx ← inline answer card for clarification interrupts
```

## Session management

Sessions are stored in `localStorage` under the key `wa-sessions`. Each session:

```ts
{
  id: string          // thread_id sent to backend
  title: string       // first user message, truncated to 50 chars
  messages: Message[] // full chat history
  createdAt: number
  updatedAt: number
}
```

## Interrupt handling

The backend can pause mid-response with two interrupt types:

| Type | Component shown | Resume via |
|------|-----------------|------------|
| `tool_approval` | `ToolApprovalCard` | Approve → `{ approved: true }` / Reject → `{ approved: false }` |
| `clarification` | `ClarificationCard` + assistant bubble | `{ answer: "..." }` |

## Local dev

```bash
npm install
npm run dev
# Opens http://localhost:5173
```

## Environment

The API base URL is hardcoded to `http://localhost:8000` in `src/api/chat.ts`.
Vite proxying is not used — CORS is handled by the FastAPI backend.
