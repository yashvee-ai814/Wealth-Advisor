from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.v1.llm import router as v1_router

app = FastAPI(title="Wealth Advisor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
