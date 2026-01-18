from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ClassSession, AttendanceLog, User
from app.api.students import enroll_student
from pathlib import Path
from jose import jwt, JWTError
from app.core.config import settings
import csv
import io

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_current_user_from_cookie(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract user from JWT cookie, return None if invalid"""
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username:
            return db.query(User).filter(User.username == username).first()
    except JWTError:
        pass
    return None

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login page for teachers"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/logout")
def logout():
    """Clear auth cookie and redirect to login"""
    response = RedirectResponse(url="/dashboard/login", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/", response_class=HTMLResponse)
def view_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    """Teacher Dashboard - Protected by cookie auth"""
    if not user:
        return RedirectResponse(url="/dashboard/login", status_code=303)
    
    sessions = db.query(ClassSession).order_by(ClassSession.start_time.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": {"username": user.username}, 
        "sessions": sessions
    })

@router.post("/enroll", response_class=HTMLResponse)
async def dashboard_enroll(
    request: Request,
    full_name: str = Form(...),
    student_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if not user:
        return RedirectResponse(url="/dashboard/login", status_code=303)
    try:
        await enroll_student(full_name, student_id, files, db)
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return f"Error: {e}"

@router.get("/session/{session_id}", response_class=HTMLResponse)
def view_session(
    session_id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if not user:
        return RedirectResponse(url="/dashboard/login", status_code=303)
    
    session = db.get(ClassSession, session_id)
    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    return templates.TemplateResponse("report.html", {
        "request": request, 
        "session": session, 
        "logs": logs
    })

@router.get("/session/{session_id}/export")
def export_session_csv(
    session_id: int, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    """Export attendance as CSV file"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Student Name", "Status", "Confidence", "Timestamp"])
    
    for log in logs:
        writer.writerow([
            log.student.student_id,
            log.student.full_name,
            log.status,
            f"{log.confidence_score:.2f}" if log.confidence_score else "N/A",
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    output.seek(0)
    filename = f"attendance_{session.course_name}_{session.start_time.strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
