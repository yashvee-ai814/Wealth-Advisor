import type { ChatResponse } from '../types/chat'

const BASE = 'http://localhost:8000'

async function parseError(res: Response): Promise<string> {
  let detail = `HTTP ${res.status}`
  try {
    const body = await res.json()
    detail = body.detail ?? detail
  } catch {
    detail = await res.text()
  }
  return detail
}

export async function sendMessage(
  session_id: string,
  message: string,
  auto_approve_tools = false,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, message, auto_approve_tools }),
  })
  if (!res.ok) throw new Error(`Chat failed: ${await parseError(res)}`)
  return res.json() as Promise<ChatResponse>
}

export async function resumeInterrupt(
  session_id: string,
  resume_input: Record<string, unknown>,
  auto_approve_tools = false,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, resume_input, auto_approve_tools }),
  })
  if (!res.ok) throw new Error(`Resume failed: ${await parseError(res)}`)
  return res.json() as Promise<ChatResponse>
}

export async function clearChat(session_id: string): Promise<void> {
  await fetch(`${BASE}/chat/${session_id}`, { method: 'DELETE' })
}
