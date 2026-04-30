export interface ToolCallInfo {
  name: string
  args: Record<string, unknown>
  result?: string
}

export interface PendingInterrupt {
  type: 'tool_approval' | 'clarification'
  tool_calls?: ToolCallInfo[]
  question?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  toolCallsUsed?: ToolCallInfo[]
  timestamp: number
}

export interface ChatResponse {
  session_id: string
  reply: string
  status: 'complete' | 'awaiting_tool_approval' | 'awaiting_clarification'
  pending_interrupt?: PendingInterrupt
  tool_calls_used: ToolCallInfo[]
}
