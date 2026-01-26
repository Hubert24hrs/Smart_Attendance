"""
Notification Service - Push notifications and alerts
Supports email and mock push notifications (Firebase-ready)
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

from app.db.database import get_db
from app.db.models import User, Student, AttendanceLog
from app.api.auth import get_current_user
from app.core.middleware import require_admin_or_above

router = APIRouter()


# =============================================================================
# ENUMS & SCHEMAS
# =============================================================================
class NotificationType(str, Enum):
    ATTENDANCE_ALERT = "attendance_alert"
    LOW_ATTENDANCE = "low_attendance"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SYSTEM = "system"


class NotificationRequest(BaseModel):
    type: NotificationType
    title: str
    message: str
    recipient_ids: Optional[List[int]] = None  # User IDs, None = all admins


class NotificationLog(BaseModel):
    id: int
    type: str
    title: str
    message: str
    sent_at: datetime
    read: bool = False


# In-memory notification storage (use Redis in production)
notification_store: dict[int, list[dict]] = {}
notification_counter = 0

# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post("/send")
async def send_notification(
    notification: NotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a notification to users"""
    require_admin_or_above(current_user)

    global notification_counter
    notification_counter += 1

    # Determine recipients
    if notification.recipient_ids:
        recipients = (
            db.query(User).filter(User.id.in_(notification.recipient_ids)).all()
        )
    else:
        # Send to all admins of the institution
        recipients = (
            db.query(User)
            .filter(User.institution_id == current_user.institution_id)
            .all()
        )

    sent_count = 0
    for user in recipients:
        if user.id not in notification_store:
            notification_store[user.id] = []

        notification_store[user.id].append(
            {
                "id": notification_counter,
                "type": notification.type.value,
                "title": notification.title,
                "message": notification.message,
                "sent_at": datetime.utcnow().isoformat(),
                "read": False,
            }
        )
        sent_count += 1

        # Send email in background if user has email
        if user.email:
            background_tasks.add_task(
                send_email_notification,
                user.email,
                notification.title,
                notification.message,
            )

    return {
        "success": True,
        "notification_id": notification_counter,
        "sent_to": sent_count,
    }


@router.get("/my")
def get_my_notifications(current_user: User = Depends(get_current_user)):
    """Get notifications for current user"""
    notifications = notification_store.get(current_user.id, [])
    return {
        "unread_count": sum(1 for n in notifications if not n["read"]),
        "notifications": sorted(
            notifications, key=lambda x: x["sent_at"], reverse=True
        )[:50],
    }


@router.post("/read/{notification_id}")
def mark_as_read(notification_id: int, current_user: User = Depends(get_current_user)):
    """Mark a notification as read"""
    notifications = notification_store.get(current_user.id, [])
    for n in notifications:
        if n["id"] == notification_id:
            n["read"] = True
            return {"success": True}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/read-all")
def mark_all_as_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read"""
    notifications = notification_store.get(current_user.id, [])
    for n in notifications:
        n["read"] = True
    return {"success": True, "marked": len(notifications)}


@router.post("/alert/low-attendance")
async def send_low_attendance_alert(
    threshold: float = 70.0,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send alerts for students with low attendance
    This would typically be called by a scheduled job
    """
    require_admin_or_above(current_user)

    institution_id = current_user.institution_id
    students = db.query(Student).filter(Student.institution_id == institution_id).all()

    alerts_sent = 0
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

        if rate < threshold and total >= 3:  # At least 3 sessions
            # Store alert
            global notification_counter
            notification_counter += 1

            if current_user.id not in notification_store:
                notification_store[current_user.id] = []

            notification_store[current_user.id].append(
                {
                    "id": notification_counter,
                    "type": NotificationType.LOW_ATTENDANCE.value,
                    "title": f"Low Attendance Alert: {student.full_name}",
                    "message": (
                        f"Student {student.full_name} has {rate:.1f}% attendance "
                        f"({present}/{total} sessions)"
                    ),
                    "sent_at": datetime.utcnow().isoformat(),
                    "read": False,
                }
            )
            alerts_sent += 1

    return {"success": True, "alerts_sent": alerts_sent, "threshold": threshold}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def send_email_notification(email: str, subject: str, message: str):
    """Background task to send email notification"""
    try:
        # Use the email service if configured
        print(f"[EMAIL] To: {email}, Subject: {subject}")
        # EmailService.send_simple_email(email, subject, message)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


# =============================================================================
# MOCK FIREBASE PUSH (Ready for real integration)
# =============================================================================
@router.post("/push/register")
def register_device_token(
    device_token: str,
    platform: str = "android",  # android, ios, web
    current_user: User = Depends(get_current_user),
):
    """
    Register FCM device token for push notifications
    In production, store in database and use Firebase Admin SDK
    """
    # Mock storage
    return {
        "success": True,
        "message": f"Device token registered for {current_user.username}",
        "platform": platform,
        "mock": True,
    }


@router.post("/push/send")
def send_push_notification(
    title: str, body: str, user_id: int, current_user: User = Depends(get_current_user)
):
    """
    Send push notification (MOCK)
    In production, use firebase_admin.messaging
    """
    require_admin_or_above(current_user)

    return {
        "success": True,
        "mock": True,
        "message": f"Push notification queued for user {user_id}",
        "title": title,
        "body": body,
    }
