from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import engine, Base

# IMPORTANT: Import models before create_all so they are registered with Base.metadata
from app.db import models  # This registers all models with Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Secure Smart Classroom Attendance System API"
)

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
from app.routers import dashboard_view

# Register Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(dashboard_view.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {
        "system": "Smart Attendance System",
        "status": "online",
        "version": settings.PROJECT_VERSION
    }
