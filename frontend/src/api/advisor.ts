import type { AdvisorRequest, AdvisorResponse } from '../types/advisor'

export async function assessRetirement(req: AdvisorRequest): Promise<AdvisorResponse> {
  const response = await fetch('http://localhost:8000/assess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail ?? detail
    } catch {
      detail = await response.text()
    }
    throw new Error(`Assessment failed: ${detail}`)
  }

  return response.json() as Promise<AdvisorResponse>
}
