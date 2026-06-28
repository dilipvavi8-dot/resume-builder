"""Resume Builder - FastAPI Backend Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routers import resume, health, export
from src.config import settings

app = FastAPI(
    title="Resume Builder API",
    description="AI-powered resume builder backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(resume.router, prefix="/api/v1", tags=["Resume"])
app.include_router(export.router, prefix="/api/v1", tags=["Export"])


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({"message": "Resume Builder API is running", "version": "1.0.0"})
