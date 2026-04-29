import httpx
import json
import re
from fastapi import HTTPException
from .models import AdvisorRequest, AdvisorResponse
from .config import settings


def build_prompt(req: AdvisorRequest) -> str:
    return f"""You are a UK pension and retirement planning expert. Analyse the following client data and provide a retirement readiness assessment.

Client Data:
- Current age: {req.age}
- Target retirement age: {req.retirement_age}
- Current annual salary: £{req.current_salary:,.0f}
- Current pension pot: £{req.current_pot:,.0f}
- Monthly personal contribution: £{req.monthly_contribution:,.0f}
- Monthly employer contribution: £{req.employer_contribution:,.0f}
- Target annual retirement income: £{req.retirement_income_goal:,.0f}

UK Pension Assumptions to use in all calculations:
- 5% annual growth after charges
- 3.5% sustainable drawdown rate
- £11,500/yr state pension from age 67
- 2.5% annual inflation

You MUST respond with ONLY a valid JSON object — no markdown, no explanation, no extra text. The JSON must exactly match this schema:

{{
  "readiness_score": <integer 0-100>,
  "readiness_label": <"On track" | "Needs attention" | "At risk">,
  "projected_pot": <float — projected pension pot value at retirement age>,
  "projected_annual_income": <float — projected annual drawdown income including state pension where applicable>,
  "shortfall": <float — max(0, retirement_income_goal - projected_annual_income)>,
  "years_to_retirement": <integer — retirement_age minus current age>,
  "summary": <string — 2-3 sentence plain English summary of the outlook>,
  "action_steps": [
    {{
      "priority": <"high" | "medium" | "low">,
      "action": <string — a specific concrete action to take>,
      "reason": <string — why this action will improve retirement readiness>
    }}
  ],
  "disclaimer": "This is not financial advice. Projections are estimates based on assumed growth rates. Please consult a qualified financial adviser."
}}

Rules:
- action_steps: 1 to 4 items, ordered by priority (high first)
- readiness_score thresholds: 70-100 → "On track", 40-69 → "Needs attention", 0-39 → "At risk"
- shortfall must equal max(0, retirement_income_goal - projected_annual_income)
- Do NOT wrap the JSON in markdown code fences
- Output ONLY the JSON object, nothing else"""


async def get_advice(req: AdvisorRequest) -> AdvisorResponse:
    prompt = build_prompt(req)

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json=payload,
            )
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Cannot reach Ollama at {settings.OLLAMA_BASE_URL}: {exc}",
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama returned an error: {exc.response.text}",
            )

    data = response.json()
    raw_content: str = data["message"]["content"]

    # Strip markdown fences that some models add despite instructions
    raw_content = re.sub(r"```json\s*", "", raw_content)
    raw_content = re.sub(r"```\s*", "", raw_content)
    raw_content = raw_content.strip()

    try:
        parsed = json.loads(raw_content)
        return AdvisorResponse(**parsed)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"LLM response was not valid JSON: {exc}. "
                f"Raw output (first 300 chars): {raw_content[:300]}"
            ),
        )
