export interface AdvisorRequest {
  age: number
  retirement_age: number
  current_salary: number
  current_pot: number
  monthly_contribution: number
  employer_contribution: number
  retirement_income_goal: number
}

export interface ActionStep {
  priority: 'high' | 'medium' | 'low'
  action: string
  reason: string
}

export interface AdvisorResponse {
  readiness_score: number
  readiness_label: 'On track' | 'Needs attention' | 'At risk'
  projected_pot: number
  projected_annual_income: number
  shortfall: number
  years_to_retirement: number
  summary: string
  action_steps: ActionStep[]
  disclaimer: string
}
