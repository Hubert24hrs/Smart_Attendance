from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.db.database import engine, Base

# IMPORTANT: Import models before create_all
from app.db import models

# Create tables
Base.metadata.create_all(bind=engine)

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Smart Attendance Platform - Multi-tenant SaaS for Schools & Institutions"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# API v1 ROUTERS
# =============================================================================
from app.api import auth, students, sessions, institutions, analytics
from app.routers import dashboard_view, admin_view

# Core API (v1)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(institutions.router, prefix="/api/v1/institutions", tags=["Institutions"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Legacy routes (backward compatibility)
app.include_router(auth.router, prefix="/auth", tags=["Auth (Legacy)"])
app.include_router(students.router, prefix="/students", tags=["Students (Legacy)"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions (Legacy)"])

# Web Dashboard (Jinja2 - will be replaced by React)
app.include_router(dashboard_view.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(admin_view.router, prefix="/admin", tags=["Admin"])

# =============================================================================
# ROOT & HEALTH
# =============================================================================
@app.get("/")
def root():
    return {
        "platform": "Smart Attendance Platform",
        "version": settings.PROJECT_VERSION,
        "status": "online",
        "docs": "/docs",
        "api_version": "v1"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
