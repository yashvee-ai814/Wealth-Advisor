import { useState, useRef, useEffect } from 'react'

export default function ChatInput({ onSend, disabled, autoApprove }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`
  }, [text])

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="shrink-0 border-t border-slate-800/80 bg-slate-900/80 backdrop-blur-xl px-4 py-3">
      {autoApprove && (
        <div className="flex items-center gap-1.5 mb-2 text-xs text-amber-400/80">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
          Auto-approve is on — tools will run automatically
        </div>
      )}
      <form onSubmit={handleSubmit} className="flex items-end gap-3">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Waiting for response…' : 'Ask about your wealth, retirement, or savings goals…'}
          disabled={disabled}
          rows={2}
          className="flex-1 resize-none px-4 py-3 text-sm bg-slate-800/80 border border-slate-700 hover:border-slate-600 focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20 rounded-2xl text-slate-200 placeholder-slate-500 focus:outline-none disabled:opacity-40 transition-colors leading-relaxed"
        />
        <button
          type="submit"
          disabled={disabled || !text.trim()}
          className="w-11 h-11 shrink-0 bg-gradient-to-br from-amber-500 to-yellow-600 hover:from-amber-400 hover:to-yellow-500 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-all duration-150 shadow-lg shadow-amber-500/20 hover:shadow-amber-500/40 hover:scale-105 active:scale-95"
          aria-label="Send"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 -rotate-90">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </form>
      <p className="text-xs text-slate-600 text-center mt-2">
        Enter to send · Shift+Enter for new line · Not financial advice
      </p>
    </div>
  )
}
