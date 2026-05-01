import { useState, useCallback, useEffect, useRef } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import ChatWindow from '../components/chat/ChatWindow.jsx'
import ChatInput from '../components/chat/ChatInput.jsx'
import { sendMessage, resumeInterrupt } from '../api/chat.ts'
import { useTheme } from '../context/ThemeContext.jsx'

const SESSIONS_KEY = 'wa-sessions'

function newSessionId() {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function loadSessions() {
  try { return JSON.parse(localStorage.getItem(SESSIONS_KEY) || '[]') } catch { return [] }
}

function AutoApproveToggle({ enabled, onChange }) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      title={enabled ? 'Auto-approve ON — tools run without asking' : 'Auto-approve OFF — you approve each tool call'}
      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border text-xs font-medium transition-all duration-200 ${
        enabled
          ? 'bg-amber-500/20 border-amber-500/50 text-amber-600 dark:text-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.15)]'
          : 'bg-white border-slate-200 text-slate-500 hover:border-slate-300 dark:bg-slate-800 dark:border-slate-600 dark:text-slate-400 dark:hover:border-slate-500'
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full transition-colors ${enabled ? 'bg-amber-400' : 'bg-slate-400 dark:bg-slate-500'}`} />
      Auto Tools {enabled ? 'ON' : 'OFF'}
    </button>
  )
}

function AiStatusBadge() {
  return (
    <span className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/50 px-2.5 py-1.5 rounded-full font-medium">
      <span className="w-1.5 h-1.5 bg-emerald-500 dark:bg-emerald-400 rounded-full animate-pulse" />
      AI Active
    </span>
  )
}

function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme()
  return (
    <button
      onClick={toggleTheme}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 bg-white hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-all duration-150"
    >
      {isDark ? (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      )}
    </button>
  )
}

export default function ChatPage() {
  const [sessions, setSessions] = useState(loadSessions)
  const [currentSessionId, setCurrentSessionId] = useState(() => newSessionId())
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [pendingInterrupt, setPendingInterrupt] = useState(null)
  const [error, setError] = useState(null)
  const [autoApprove, setAutoApprove] = useState(false)

  // Ref so handlers always see the current session ID without stale closures.
  const currentSessionIdRef = useRef(currentSessionId)

  useEffect(() => {
    if (messages.length === 0) return
    const id = currentSessionIdRef.current
    const title = (messages.find((m) => m.role === 'user')?.content ?? 'New conversation').slice(0, 50)
    setSessions((prev) => {
      const idx = prev.findIndex((s) => s.id === id)
      const session = {
        id,
        title,
        messages,
        createdAt: idx >= 0 ? prev[idx].createdAt : Date.now(),
        updatedAt: Date.now(),
      }
      const updated = idx >= 0 ? prev.map((s) => (s.id === id ? session : s)) : [session, ...prev]
      localStorage.setItem(SESSIONS_KEY, JSON.stringify(updated))
      return updated
    })
  }, [messages])

  const handleResponse = useCallback((response) => {
    const newMsgs = []

    const toolsWithResults = (response.tool_calls_used ?? []).filter((tc) => tc.result)
    if (toolsWithResults.length > 0) {
      newMsgs.push({ role: 'tool_calls', tools: toolsWithResults, timestamp: Date.now() })
    }

    if (response.reply) {
      newMsgs.push({
        role: 'assistant',
        content: response.reply,
        toolCallsUsed: response.tool_calls_used ?? [],
        timestamp: Date.now(),
      })
    }

    if (response.status === 'awaiting_clarification' && response.pending_interrupt?.question) {
      newMsgs.push({
        role: 'assistant',
        content: response.pending_interrupt.question,
        isQuestion: true,
        timestamp: Date.now(),
      })
    }

    if (newMsgs.length > 0) setMessages((prev) => [...prev, ...newMsgs])

    setPendingInterrupt(response.status === 'complete' ? null : response.pending_interrupt ?? null)
  }, [])

  const handleSend = useCallback(async (text) => {
    setError(null)
    setMessages((prev) => [...prev, { role: 'user', content: text, timestamp: Date.now() }])
    setLoading(true)
    setPendingInterrupt(null)
    try {
      handleResponse(await sendMessage(currentSessionIdRef.current, text, autoApprove))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, [handleResponse, autoApprove])

  const handleApprove = useCallback(async () => {
    setError(null)
    setLoading(true)
    setPendingInterrupt(null)
    try {
      handleResponse(await resumeInterrupt(currentSessionIdRef.current, { approved: true }, autoApprove))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, [handleResponse, autoApprove])

  const handleReject = useCallback(async () => {
    setError(null)
    setLoading(true)
    setPendingInterrupt(null)
    try {
      handleResponse(await resumeInterrupt(currentSessionIdRef.current, { approved: false }, false))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, [handleResponse])

  const handleAnswer = useCallback(async (answer) => {
    setError(null)
    setMessages((prev) => [...prev, { role: 'user', content: answer, timestamp: Date.now() }])
    setLoading(true)
    setPendingInterrupt(null)
    try {
      handleResponse(await resumeInterrupt(currentSessionIdRef.current, { answer }, autoApprove))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, [handleResponse, autoApprove])

  const handleNewChat = useCallback(() => {
    const id = newSessionId()
    currentSessionIdRef.current = id
    setCurrentSessionId(id)
    setMessages([])
    setPendingInterrupt(null)
    setError(null)
  }, [])

  const handleSelectSession = useCallback((id) => {
    const session = sessions.find((s) => s.id === id)
    if (!session) return
    currentSessionIdRef.current = id
    setCurrentSessionId(id)
    setMessages(session.messages || [])
    setPendingInterrupt(null)
    setError(null)
  }, [sessions])

  const handleDeleteSession = useCallback((id) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== id)
      localStorage.setItem(SESSIONS_KEY, JSON.stringify(updated))
      return updated
    })
    if (id === currentSessionIdRef.current) handleNewChat()
  }, [handleNewChat])

  const currentSession = sessions.find((s) => s.id === currentSessionId)
  const inputDisabled = loading || pendingInterrupt?.type === 'tool_approval'
  const onSend = pendingInterrupt?.type === 'clarification' ? handleAnswer : handleSend

  return (
    <AppLayout
      sessions={sessions}
      currentSessionId={currentSessionId}
      sessionTitle={currentSession?.title ?? null}
      onNewChat={handleNewChat}
      onSelectSession={handleSelectSession}
      onDeleteSession={handleDeleteSession}
      error={error}
      onDismissError={() => setError(null)}
      headerRight={
        <>
          <AutoApproveToggle enabled={autoApprove} onChange={setAutoApprove} />
          <AiStatusBadge />
          <ThemeToggle />
        </>
      }
    >
      <div className="flex-1 flex flex-col overflow-hidden max-w-4xl w-full mx-auto px-0 sm:px-2">
        <ChatWindow
          messages={messages}
          pendingInterrupt={pendingInterrupt}
          loading={loading}
          onApprove={handleApprove}
          onReject={handleReject}
          onSend={onSend}
        />
        <ChatInput onSend={onSend} disabled={inputDisabled} autoApprove={autoApprove} />
      </div>
    </AppLayout>
  )
}
