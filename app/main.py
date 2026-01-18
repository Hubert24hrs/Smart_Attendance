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
    description="Secure Smart Classroom Attendance System API"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api import auth, students, sessions
from app.routers import dashboard_view, admin_view

# Register Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(dashboard_view.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(admin_view.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def root():
    return {
        "system": "Smart Attendance System",
        "status": "online",
        "version": settings.PROJECT_VERSION
    }
