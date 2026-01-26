from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Student, Course, ClassSession
from app.core.security import get_password_hash
from app.routers.dashboard_view import get_current_user_from_cookie
from pathlib import Path
from typing import Optional

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def require_admin(user: Optional[User]) -> User:
    """Middleware to require admin role"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    """Admin Dashboard - Overview of system"""
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    teachers = db.query(User).filter(User.role == "teacher").all()
    students = db.query(Student).all()
    courses = db.query(Course).all()
    sessions = (
        db.query(ClassSession).order_by(ClassSession.start_time.desc()).limit(10).all()
    )

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "teachers": teachers,
            "students": students,
            "courses": courses,
            "recent_sessions": sessions,
            "stats": {
                "total_teachers": len(teachers),
                "total_students": len(students),
                "total_courses": len(courses),
            },
        },
    )


@router.get("/teachers", response_class=HTMLResponse)
def list_teachers(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    teachers = db.query(User).filter(User.role == "teacher").all()
    return templates.TemplateResponse(
        "admin/teachers.html", {"request": request, "user": user, "teachers": teachers}
    )


@router.post("/teachers/add")
def add_teacher(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_teacher = User(
        username=username, hashed_password=get_password_hash(password), role="teacher"
    )
    db.add(new_teacher)
    db.commit()
    return RedirectResponse(url="/admin/teachers", status_code=303)


@router.get("/courses", response_class=HTMLResponse)
def list_courses(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    courses = db.query(Course).all()
    teachers = db.query(User).filter(User.role == "teacher").all()

    return templates.TemplateResponse(
        "admin/courses.html",
        {"request": request, "user": user, "courses": courses, "teachers": teachers},
    )


@router.post("/courses/add")
def add_course(
    code: str = Form(...),
    name: str = Form(...),
    teacher_id: int = Form(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    new_course = Course(code=code, name=name, teacher_id=teacher_id)
    db.add(new_course)
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)


@router.get("/students", response_class=HTMLResponse)
def list_students_admin(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    students = db.query(Student).all()
    return templates.TemplateResponse(
        "admin/students.html", {"request": request, "user": user, "students": students}
    )


@router.post("/students/{student_id}/delete")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/login", status_code=303)

    student = db.get(Student, student_id)
    if student:
        db.delete(student)
        db.commit()
    return RedirectResponse(url="/admin/students", status_code=303)
