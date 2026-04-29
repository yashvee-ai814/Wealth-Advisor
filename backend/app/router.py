from fastapi import APIRouter
from .models import AdvisorRequest, AdvisorResponse
from .llm import get_advice
from .config import settings

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}


@router.post("/assess", response_model=AdvisorResponse)
async def assess(req: AdvisorRequest) -> AdvisorResponse:
    return await get_advice(req)
