from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.types import interrupt


# ── Input / Output models ────────────────────────────────────────────────────

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


# ── Tool definitions ─────────────────────────────────────────────────────────

@tool(args_schema=ProjectedPotInput)
def calculate_projected_pot(
    current_pot: float,
    monthly_personal: float,
    monthly_employer: float,
    annual_growth_rate: float,
    years: int,
) -> dict:
    """
    Calculate the projected pension pot at retirement using the future value annuity formula.
    Use this when the user provides their current savings, contributions, and retirement timeline.
    Always call this before calculating drawdown income or readiness score.
    Formula: FV = PV*(1+r)^n + PMT_annual*((1+r)^n - 1)/r
    """
    r = annual_growth_rate
    n = years
    pmt_annual = (monthly_personal + monthly_employer) * 12
    growth_factor = (1 + r) ** n
    projected_pot = current_pot * growth_factor + pmt_annual * (growth_factor - 1) / r
    total_contributions = current_pot + pmt_annual * n
    total_growth = projected_pot - total_contributions
    return ProjectedPotOutput(
        projected_pot=round(projected_pot, 2),
        total_contributions=round(total_contributions, 2),
        total_growth=round(total_growth, 2),
    ).model_dump()


@tool(args_schema=DrawdownIncomeInput)
def calculate_drawdown_income(
    pot_value: float,
    drawdown_rate: float,
    state_pension_annual: float,
) -> dict:
    """
    Calculate projected annual retirement income from a pension pot using sustainable drawdown.
    Use this after projecting the pot size to determine what annual income it will generate.
    Formula: annual_income = pot * drawdown_rate + state_pension
    """
    drawdown_from_pot = pot_value * drawdown_rate
    annual_income = drawdown_from_pot + state_pension_annual
    return DrawdownIncomeOutput(
        annual_income=round(annual_income, 2),
        drawdown_from_pot=round(drawdown_from_pot, 2),
        state_pension_contribution=round(state_pension_annual, 2),
    ).model_dump()


@tool(args_schema=MonthlySavingsInput)
def calculate_monthly_savings_needed(
    target_pot: float,
    current_pot: float,
    annual_growth_rate: float,
    years: int,
) -> dict:
    """
    Calculate how much the user needs to save monthly to reach a target pension pot.
    Use this when the user asks 'how much should I save?' or wants to work backwards from a goal.
    Formula: PMT = (target - PV*(1+r)^n) * r / ((1+r)^n - 1) / 12
    """
    r = annual_growth_rate
    n = years
    growth_factor = (1 + r) ** n
    remaining = target_pot - current_pot * growth_factor
    if remaining <= 0:
        monthly = 0.0
    else:
        monthly = remaining * r / (growth_factor - 1) / 12
    return MonthlySavingsOutput(
        monthly_savings_needed=round(max(0.0, monthly), 2),
        total_to_accumulate=round(max(0.0, remaining), 2),
    ).model_dump()


@tool(args_schema=ShortfallInput)
def calculate_shortfall(
    income_goal: float,
    projected_annual_income: float,
) -> dict:
    """
    Calculate the annual income shortfall between the user's goal and projected income.
    Use this after calculating projected income to quantify the gap (or surplus).
    Formula: shortfall = max(0, income_goal - projected_income)
    """
    diff = income_goal - projected_annual_income
    shortfall = max(0.0, diff)
    surplus = max(0.0, -diff)
    return ShortfallOutput(
        shortfall=round(shortfall, 2),
        surplus=round(surplus, 2),
        is_on_track=shortfall == 0.0,
    ).model_dump()


@tool(args_schema=ReadinessScoreInput)
def calculate_readiness_score(
    projected_income: float,
    income_goal: float,
) -> dict:
    """
    Calculate a retirement readiness score from 0-100 and a readiness label.
    Use this as a summary metric after all other calculations are complete.
    Score >= 70 = 'On track', 40-69 = 'Needs attention', < 40 = 'At risk'.
    Formula: score = min(100, int(projected / goal * 100))
    """
    score = min(100, int(projected_income / income_goal * 100))
    label = "On track" if score >= 70 else "Needs attention" if score >= 40 else "At risk"
    return ReadinessScoreOutput(score=score, label=label).model_dump()


@tool(args_schema=InflationAdjustedGoalInput)
def calculate_inflation_adjusted_goal(
    current_goal: float,
    inflation_rate: float,
    years: int,
) -> dict:
    """
    Adjust the user's income goal for inflation to express it in future money.
    Use this when the user states a retirement income goal in today's money so it can be
    compared fairly with projected future income.
    Formula: adjusted = current_goal * (1 + inflation_rate)^years
    """
    adjusted_goal = current_goal * ((1 + inflation_rate) ** years)
    uplift = adjusted_goal - current_goal
    return InflationAdjustedGoalOutput(
        adjusted_goal=round(adjusted_goal, 2),
        inflation_uplift=round(uplift, 2),
    ).model_dump()


@tool(args_schema=StatePensionInput)
def get_uk_state_pension_info(
    current_age: int,
    retirement_age: int,
) -> dict:
    """
    Get UK state pension eligibility and annual amount based on the user's ages.
    The full new UK state pension is £11,502/year, payable from age 67.
    Use this whenever state pension needs to be factored into retirement income calculations.
    """
    STATE_PENSION_AGE = 67
    FULL_ANNUAL_STATE_PENSION = 11502.0

    if retirement_age < STATE_PENSION_AGE:
        annual_amount = 0.0
        note = (
            f"No state pension at planned retirement age {retirement_age}. "
            f"State pension starts at age {STATE_PENSION_AGE}."
        )
    else:
        annual_amount = FULL_ANNUAL_STATE_PENSION
        note = f"Full new UK state pension of £{FULL_ANNUAL_STATE_PENSION:,.0f}/yr from age {STATE_PENSION_AGE}."

    return StatePensionOutput(
        annual_state_pension=annual_amount,
        eligible_from_age=STATE_PENSION_AGE,
        years_until_eligible=max(0, STATE_PENSION_AGE - current_age),
        note=note,
    ).model_dump()


@tool(args_schema=AskHumanInput)
def ask_human(question: str) -> str:
    """
    Pause the workflow and ask the user a clarifying question.
    Use this when you are missing critical information needed to perform a calculation,
    such as the user's age, income, savings amount, or retirement goal.
    Do NOT guess missing values — always ask.
    """
    return interrupt(question)


ALL_TOOLS = [
    calculate_projected_pot,
    calculate_drawdown_income,
    calculate_monthly_savings_needed,
    calculate_shortfall,
    calculate_readiness_score,
    calculate_inflation_adjusted_goal,
    get_uk_state_pension_info,
    ask_human,
]
