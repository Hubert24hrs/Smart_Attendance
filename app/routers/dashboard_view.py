from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ClassSession, AttendanceLog
from app.api.auth import get_current_user
from app.api.students import enroll_student # Reuse logic
from pathlib import Path

router = APIRouter()
# Use absolute path for templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse)
def view_dashboard(request: Request, db: Session = Depends(get_db)):
    """Teacher Dashboard - Shows enrollment form and session list"""
    sessions = db.query(ClassSession).order_by(ClassSession.start_time.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": {"username": "Teacher"}, 
        "sessions": sessions
    })

@router.post("/enroll", response_class=HTMLResponse)
async def dashboard_enroll(
    request: Request,
    full_name: str = Form(...),
    student_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        await enroll_student(full_name, student_id, files, db)
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return f"Error: {e}"

@router.get("/session/{session_id}", response_class=HTMLResponse)
def view_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = db.get(ClassSession, session_id)
    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    return templates.TemplateResponse("report.html", {
        "request": request, 
        "session": session, 
        "logs": logs
    })
