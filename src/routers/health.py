"""Health check endpoints"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time

router = APIRouter()

START_TIME = time.time()


@router.get("/health", summary="Health check")
async def health_check():
    uptime = round(time.time() - START_TIME, 2)
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "uptime_seconds": uptime,
            "service": "resume-builder-api",
            "version": "1.0.0",
        },
    )


@router.get("/ready", summary="Readiness check")
async def readiness_check():
    return JSONResponse(status_code=200, content={"status": "ready"})
