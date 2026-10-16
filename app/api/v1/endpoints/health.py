from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):  # noqa: B008
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:  # noqa: BLE001
        db_status = f"unhealthy: {e!s}"

    return {
        "status": "online" if db_status == "healthy" else "degraded",
        "database": db_status,
        "service": "rag-enterprise-engine",
    }
