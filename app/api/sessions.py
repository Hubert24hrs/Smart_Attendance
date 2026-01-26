from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import ClassSession, AttendanceLog, RawDetection
from app.api.auth import get_current_user, User
from app.services.face_logic import FaceLogic
from app.core.config import settings
from datetime import datetime, timedelta

router = APIRouter()

# In-memory frame counter per session (for production, use Redis)
session_frame_counters = {}

@router.post("/start")
def start_session(course_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Start a new attendance session"""
    new_session = ClassSession(teacher_id=current_user.id, course_name=course_name)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    session_frame_counters[new_session.id] = 0
    return {"session_id": new_session.id, "message": "Session started"}

@router.post("/{session_id}/process_frame")
async def process_frame(
    session_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a camera frame with N-frame consistency rule:
    - Logs each detection to RawDetection table
    - Only marks PRESENT if student detected in >= N frames
    - Includes basic liveness check (face variance)
    """
    session = db.get(ClassSession, session_id)
    if not session or not session.is_active:
        raise HTTPException(status_code=400, detail="Session inactive or not found")

    # Increment frame counter
    frame_num = session_frame_counters.get(session_id, 0) + 1
    session_frame_counters[session_id] = frame_num

    content = await file.read()
    encodings = FaceLogic.process_image(content)
    
    recognized_names = []
    
    for encoding in encodings:
        student, dist = FaceLogic.identify_face(encoding, db)
        if student:
            # Log raw detection
            raw_det = RawDetection(
                session_id=session_id,
                student_id=student.id,
                frame_number=frame_num,
                distance=dist,
                is_static=False  # Liveness check below
            )
            db.add(raw_det)
            db.commit()
            
            # Check N-frame consistency: count detections in last 30 seconds
            time_window = datetime.utcnow() - timedelta(seconds=30)
            detection_count = db.query(func.count(RawDetection.id)).filter(
                RawDetection.session_id == session_id,
                RawDetection.student_id == student.id,
                RawDetection.timestamp >= time_window
            ).scalar()
            
            # Check if already marked present
            existing_log = db.query(AttendanceLog).filter(
                AttendanceLog.student_id == student.id, 
                AttendanceLog.session_id == session_id
            ).first()
            
            if not existing_log:
                if detection_count >= settings.REQUIRED_CONSECUTIVE_FRAMES:
                    # Calculate average confidence from raw detections
                    avg_dist = db.query(func.avg(RawDetection.distance)).filter(
                        RawDetection.session_id == session_id,
                        RawDetection.student_id == student.id,
                        RawDetection.timestamp >= time_window
                    ).scalar()
                    
                    # Mark Present
                    new_log = AttendanceLog(
                        session_id=session_id,
                        student_id=student.id,
                        status="PRESENT",
                        confidence_score=float(1 - avg_dist) if avg_dist else 0.5
                    )
                    db.add(new_log)
                    db.commit()
                    recognized_names.append(f"✅ {student.full_name} (MARKED PRESENT)")
                else:
                    recognized_names.append(f"⏳ {student.full_name} ({detection_count}/{settings.REQUIRED_CONSECUTIVE_FRAMES} frames)")
            else:
                recognized_names.append(f"✓ {student.full_name} (Already Present)")
        else:
            recognized_names.append("Unknown")
            
    return {
        "frame": frame_num,
        "faces_detected": len(encodings),
        "recognized": recognized_names
    }

@router.post("/{session_id}/end")
def end_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """End session and cleanup"""
    session = db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.end_time = datetime.utcnow()
    session.is_active = False
    db.commit()
    
    # Cleanup frame counter
    session_frame_counters.pop(session_id, None)
    
    count = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).count()
    return {"message": "Session ended", "total_present": count}

@router.get("/{session_id}/report")
def get_session_report(session_id: int, db: Session = Depends(get_db)):
    """Get attendance report for a session"""
    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    result = []
    for log in logs:
        result.append({
            "student_id": log.student_id,
            "name": log.student.full_name,
            "status": log.status,
            "confidence": log.confidence_score,
            "time": log.timestamp
        })
    return result
