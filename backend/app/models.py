from pydantic import BaseModel, Field
from typing import Literal


class AdvisorRequest(BaseModel):
    age: int = Field(ge=18, le=79)
    retirement_age: int = Field(ge=51, le=80)
    current_salary: float = Field(gt=0)
    current_pot: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    employer_contribution: float = Field(ge=0)
    retirement_income_goal: float = Field(gt=0)


class ActionStep(BaseModel):
    priority: Literal["high", "medium", "low"]
    action: str
    reason: str


class AdvisorResponse(BaseModel):
    readiness_score: int = Field(ge=0, le=100)
    readiness_label: Literal["On track", "Needs attention", "At risk"]
    projected_pot: float
    projected_annual_income: float
    shortfall: float
    years_to_retirement: int
    summary: str
    action_steps: list[ActionStep] = Field(max_length=4)
    disclaimer: str
