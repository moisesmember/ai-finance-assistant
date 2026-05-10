from fastapi import FastAPI

from app.core.config import get_settings
from app.infrastructure.api.routers import accounts, insights, transactions


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend MVP para importacao, historico e insights financeiros pessoais.",
)

app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(insights.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
