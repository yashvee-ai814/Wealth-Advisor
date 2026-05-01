function parseInline(text, keyPrefix = '') {
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g
  const parts = []
  let lastIndex = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index))
    }
    if (match[2]) {
      parts.push(<strong key={`${keyPrefix}-b-${match.index}`} className="font-semibold text-amber-300">{match[2]}</strong>)
    } else if (match[3]) {
      parts.push(<em key={`${keyPrefix}-i-${match.index}`} className="italic text-slate-300">{match[3]}</em>)
    } else if (match[4]) {
      parts.push(<code key={`${keyPrefix}-c-${match.index}`} className="bg-slate-700 text-amber-300 px-1.5 py-0.5 rounded font-mono text-xs">{match[4]}</code>)
    }
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < text.length) parts.push(text.slice(lastIndex))
  return parts.length > 0 ? parts : [text]
}

function renderLines(content) {
  const lines = content.split('\n')
  const elements = []
  let bulletBuf = []
  let numberedBuf = []
  let key = 0

  const flushBullets = () => {
    if (!bulletBuf.length) return
    elements.push(
      <ul key={key++} className="space-y-1.5 my-2">
        {bulletBuf.map((item, j) => (
          <li key={j} className="flex gap-2 items-start text-sm text-slate-200 leading-relaxed">
            <span className="text-amber-400 mt-0.5 shrink-0">◆</span>
            <span>{parseInline(item, `b${j}`)}</span>
          </li>
        ))}
      </ul>
    )
    bulletBuf = []
  }

  const flushNumbered = () => {
    if (!numberedBuf.length) return
    elements.push(
      <ol key={key++} className="space-y-1.5 my-2">
        {numberedBuf.map((item, j) => (
          <li key={j} className="flex gap-2 items-start text-sm text-slate-200 leading-relaxed">
            <span className="text-amber-400 font-semibold shrink-0 min-w-[1.25rem]">{j + 1}.</span>
            <span>{parseInline(item, `n${j}`)}</span>
          </li>
        ))}
      </ol>
    )
    numberedBuf = []
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line.startsWith('### ')) {
      flushBullets(); flushNumbered()
      elements.push(<h3 key={key++} className="text-sm font-semibold text-amber-300 mt-3 mb-1">{line.slice(4)}</h3>)
    } else if (line.startsWith('## ')) {
      flushBullets(); flushNumbered()
      elements.push(<h2 key={key++} className="text-base font-bold text-amber-400 mt-3 mb-1">{line.slice(3)}</h2>)
    } else if (line.startsWith('# ')) {
      flushBullets(); flushNumbered()
      elements.push(<h1 key={key++} className="text-lg font-bold text-amber-400 mt-3 mb-1 font-display">{line.slice(2)}</h1>)
    } else if (/^[-*] /.test(line)) {
      flushNumbered()
      bulletBuf.push(line.slice(2))
    } else if (/^\d+\. /.test(line)) {
      flushBullets()
      numberedBuf.push(line.replace(/^\d+\. /, ''))
    } else if (line.trim() === '') {
      flushBullets(); flushNumbered()
      if (elements.length > 0) elements.push(<div key={key++} className="h-1.5" />)
    } else {
      flushBullets(); flushNumbered()
      elements.push(
        <p key={key++} className="text-sm text-slate-200 leading-relaxed">
          {parseInline(line, `p${i}`)}
        </p>
      )
    }
  }

  flushBullets(); flushNumbered()
  return elements
}

export default function FormattedMessage({ content, isUser }) {
  if (isUser) {
    return <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
  }

  return <div className="space-y-0.5">{renderLines(content.trim())}</div>
}
