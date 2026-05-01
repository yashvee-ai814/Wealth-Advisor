"""Pydantic input/output models for every MCP tool."""

from pydantic import BaseModel, Field


class ProjectedPotInput(BaseModel):
    current_pot: float = Field(ge=0, description="Current pension pot value in GBP")
    monthly_personal: float = Field(ge=0, description="Monthly personal contribution in GBP")
    monthly_employer: float = Field(ge=0, description="Monthly employer contribution in GBP")
    annual_growth_rate: float = Field(gt=0, le=1, description="Expected annual growth rate as a decimal, e.g. 0.05 for 5%")
    years: int = Field(gt=0, description="Number of years until retirement")


class ProjectedPotOutput(BaseModel):
    projected_pot: float
    total_contributions: float
    total_growth: float
    formula: str = "FV = PV*(1+r)^n + PMT_annual*((1+r)^n - 1)/r"


class DrawdownIncomeInput(BaseModel):
    pot_value: float = Field(gt=0, description="Total pension pot value in GBP at retirement")
    drawdown_rate: float = Field(gt=0, le=1, description="Annual drawdown rate as decimal, e.g. 0.035 for 3.5%")
    state_pension_annual: float = Field(ge=0, description="Annual UK state pension amount in GBP (0 if not yet eligible)")


class DrawdownIncomeOutput(BaseModel):
    annual_income: float
    drawdown_from_pot: float
    state_pension_contribution: float
    formula: str = "annual_income = pot * drawdown_rate + state_pension"


class MonthlySavingsInput(BaseModel):
    target_pot: float = Field(gt=0, description="Target pension pot value at retirement in GBP")
    current_pot: float = Field(ge=0, description="Current pension pot value in GBP")
    annual_growth_rate: float = Field(gt=0, le=1, description="Expected annual growth rate as decimal")
    years: int = Field(gt=0, description="Number of years until retirement")


class MonthlySavingsOutput(BaseModel):
    monthly_savings_needed: float
    total_to_accumulate: float
    formula: str = "PMT = (target - PV*(1+r)^n) * r / ((1+r)^n - 1) / 12"


class ShortfallInput(BaseModel):
    income_goal: float = Field(gt=0, description="Target annual retirement income in GBP")
    projected_annual_income: float = Field(ge=0, description="Projected annual retirement income in GBP")


class ShortfallOutput(BaseModel):
    shortfall: float
    surplus: float
    is_on_track: bool
    formula: str = "shortfall = max(0, income_goal - projected_income)"


class ReadinessScoreInput(BaseModel):
    projected_income: float = Field(ge=0, description="Projected annual retirement income in GBP")
    income_goal: float = Field(gt=0, description="Target annual retirement income in GBP")


class ReadinessScoreOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    label: str
    formula: str = "score = min(100, int(projected/goal * 100))"


class InflationAdjustedGoalInput(BaseModel):
    current_goal: float = Field(gt=0, description="Current annual income goal in GBP in today's money")
    inflation_rate: float = Field(gt=0, le=1, description="Annual inflation rate as decimal, e.g. 0.025 for 2.5%")
    years: int = Field(gt=0, description="Number of years until retirement")


class InflationAdjustedGoalOutput(BaseModel):
    adjusted_goal: float
    inflation_uplift: float
    formula: str = "FV = current_goal * (1 + inflation_rate)^years"


class StatePensionInput(BaseModel):
    current_age: int = Field(ge=18, le=79, description="Current age in years")
    retirement_age: int = Field(ge=51, le=80, description="Planned retirement age")


class StatePensionOutput(BaseModel):
    annual_state_pension: float
    eligible_from_age: int
    years_until_eligible: int
    note: str


class AskHumanInput(BaseModel):
    question: str = Field(min_length=1, description="The clarifying question to ask the user")
