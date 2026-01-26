"""
Analytics API - Attendance trends and statistics
/api/v1/analytics/
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import User, Course, Student, ClassSession, AttendanceLog, UserRole
from app.api.auth import get_current_user
from app.core.middleware import require_admin_or_above

router = APIRouter()


# =============================================================================
# SCHEMAS
# =============================================================================
class DailyStats(BaseModel):
    date: str
    total_sessions: int
    total_present: int
    total_absent: int
    attendance_rate: float


class CourseStats(BaseModel):
    course_id: int
    course_name: str
    total_sessions: int
    avg_attendance_rate: float


class StudentAttendance(BaseModel):
    student_id: int
    student_name: str
    total_sessions: int
    sessions_present: int
    attendance_rate: float


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.get("/overview")
def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attendance overview for past N days"""
    require_admin_or_above(current_user)

    institution_id = current_user.institution_id
    start_date = datetime.utcnow() - timedelta(days=days)

    # Base query for institution's sessions
    if current_user.role == UserRole.SUPER_ADMIN.value:
        sessions_query = db.query(ClassSession).filter(
            ClassSession.start_time >= start_date
        )
    else:
        sessions_query = (
            db.query(ClassSession)
            .join(Course)
            .filter(
                Course.institution_id == institution_id,
                ClassSession.start_time >= start_date,
            )
        )

    total_sessions = sessions_query.count()

    # Attendance counts
    if current_user.role == UserRole.SUPER_ADMIN.value:
        logs_query = (
            db.query(AttendanceLog)
            .join(ClassSession)
            .filter(ClassSession.start_time >= start_date)
        )
    else:
        logs_query = (
            db.query(AttendanceLog)
            .join(ClassSession)
            .join(Course)
            .filter(
                Course.institution_id == institution_id,
                ClassSession.start_time >= start_date,
            )
        )

    total_present = logs_query.filter(AttendanceLog.status == "PRESENT").count()
    total_absent = logs_query.filter(AttendanceLog.status == "ABSENT").count()
    total_late = logs_query.filter(AttendanceLog.status == "LATE").count()

    total_records = total_present + total_absent + total_late
    attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0

    return {
        "period_days": days,
        "total_sessions": total_sessions,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_late": total_late,
        "overall_attendance_rate": round(attendance_rate, 2),
    }


@router.get("/daily", response_model=List[DailyStats])
def get_daily_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get daily attendance statistics"""
    require_admin_or_above(current_user)

    institution_id = current_user.institution_id
    results = []

    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())

        # Query sessions for this day
        if current_user.role == UserRole.SUPER_ADMIN.value:
            day_sessions = (
                db.query(ClassSession)
                .filter(ClassSession.start_time.between(start, end))
                .count()
            )
            day_present = (
                db.query(AttendanceLog)
                .join(ClassSession)
                .filter(
                    ClassSession.start_time.between(start, end),
                    AttendanceLog.status == "PRESENT",
                )
                .count()
            )
            day_absent = (
                db.query(AttendanceLog)
                .join(ClassSession)
                .filter(
                    ClassSession.start_time.between(start, end),
                    AttendanceLog.status == "ABSENT",
                )
                .count()
            )
        else:
            day_sessions = (
                db.query(ClassSession)
                .join(Course)
                .filter(
                    Course.institution_id == institution_id,
                    ClassSession.start_time.between(start, end),
                )
                .count()
            )
            day_present = (
                db.query(AttendanceLog)
                .join(ClassSession)
                .join(Course)
                .filter(
                    Course.institution_id == institution_id,
                    ClassSession.start_time.between(start, end),
                    AttendanceLog.status == "PRESENT",
                )
                .count()
            )
            day_absent = (
                db.query(AttendanceLog)
                .join(ClassSession)
                .join(Course)
                .filter(
                    Course.institution_id == institution_id,
                    ClassSession.start_time.between(start, end),
                    AttendanceLog.status == "ABSENT",
                )
                .count()
            )

        total = day_present + day_absent
        rate = (day_present / total * 100) if total > 0 else 0

        results.append(
            DailyStats(
                date=date.isoformat(),
                total_sessions=day_sessions,
                total_present=day_present,
                total_absent=day_absent,
                attendance_rate=round(rate, 2),
            )
        )

    return results


@router.get("/courses", response_model=List[CourseStats])
def get_course_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get attendance statistics per course"""
    require_admin_or_above(current_user)

    institution_id = current_user.institution_id

    if current_user.role == UserRole.SUPER_ADMIN.value:
        courses = db.query(Course).all()
    else:
        courses = db.query(Course).filter(Course.institution_id == institution_id).all()

    results = []
    for course in courses:
        sessions = (
            db.query(ClassSession).filter(ClassSession.course_id == course.id).all()
        )
        total_sessions = len(sessions)

        if total_sessions == 0:
            results.append(
                CourseStats(
                    course_id=course.id,
                    course_name=course.name,
                    total_sessions=0,
                    avg_attendance_rate=0,
                )
            )
            continue

        total_present = 0
        total_records = 0
        for session in sessions:
            present = (
                db.query(AttendanceLog)
                .filter(
                    AttendanceLog.session_id == session.id,
                    AttendanceLog.status == "PRESENT",
                )
                .count()
            )
            all_logs = (
                db.query(AttendanceLog)
                .filter(AttendanceLog.session_id == session.id)
                .count()
            )
            total_present += present
            total_records += all_logs

        avg_rate = (total_present / total_records * 100) if total_records > 0 else 0

        results.append(
            CourseStats(
                course_id=course.id,
                course_name=course.name,
                total_sessions=total_sessions,
                avg_attendance_rate=round(avg_rate, 2),
            )
        )

    return results


@router.get("/students/low-attendance")
def get_low_attendance_students(
    threshold: float = Query(70.0, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get students with attendance below threshold"""
    require_admin_or_above(current_user)

    institution_id = current_user.institution_id

    if current_user.role == UserRole.SUPER_ADMIN.value:
        students = db.query(Student).all()
    else:
        students = (
            db.query(Student).filter(Student.institution_id == institution_id).all()
        )

    low_attendance = []
    for student in students:
        total = (
            db.query(AttendanceLog)
            .filter(AttendanceLog.student_id == student.id)
            .count()
        )
        present = (
            db.query(AttendanceLog)
            .filter(
                AttendanceLog.student_id == student.id,
                AttendanceLog.status == "PRESENT",
            )
            .count()
        )

        rate = (present / total * 100) if total > 0 else 100

        if rate < threshold:
            low_attendance.append(
                {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "total_sessions": total,
                    "sessions_present": present,
                    "attendance_rate": round(rate, 2),
                }
            )

    return sorted(low_attendance, key=lambda x: x["attendance_rate"])
