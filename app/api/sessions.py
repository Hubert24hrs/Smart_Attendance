from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ClassSession, AttendanceLog, Student
from app.api.auth import get_current_user, User
from app.services.face_logic import FaceLogic
from datetime import datetime

router = APIRouter()

@router.post("/start")
def start_session(course_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Deactivate old sessions for this teacher? (Optional, skipping for MVP)
    new_session = ClassSession(teacher_id=current_user.id, course_name=course_name)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id, "message": "Session started"}

@router.post("/{session_id}/process_frame")
async def process_frame(
    session_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Receives a snapshot from the teacher's camera.
    Detects faces -> Matches -> Logs to Attendance Logic.
    """
    session = db.get(ClassSession, session_id)
    if not session or not session.is_active:
        raise HTTPException(status_code=400, detail="Session inactive or not found")

    content = await file.read()
    # 1. Detect
    encodings = FaceLogic.process_image(content)
    
    recognized_names = []
    
    # 2. Identify
    for encoding in encodings:
        student, dist = FaceLogic.identify_face(encoding, db)
        if student:
            # 3. Log (Simplistic 'Mark Present' logic for now)
            # In a real system, we'd add to a 'RawDetections' table and aggregate later.
            # Here, we'll just check if already marked present.
            
            existing_log = db.query(AttendanceLog).filter(
                AttendanceLog.student_id == student.id, 
                AttendanceLog.session_id == session_id
            ).first()
            
            if not existing_log:
                # Mark Present
                new_log = AttendanceLog(
                    session_id=session_id,
                    student_id=student.id,
                    status="PRESENT",
                    confidence_score=float(1 - dist) # Rough confidence approximation
                )
                db.add(new_log)
                db.commit()
                recognized_names.append(student.full_name)
            else:
                recognized_names.append(f"{student.full_name} (Already Marked)")
        else:
            recognized_names.append("Unknown")
            
    return {
        "faces_detected": len(encodings),
        "recognized": recognized_names
    }

@router.post("/{session_id}/end")
def end_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.end_time = datetime.utcnow()
    session.is_active = False
    db.commit()
    
    # Generate Summary
    count = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).count()
    return {"message": "Session ended", "total_present": count}

@router.get("/{session_id}/report")
def get_session_report(session_id: int, db: Session = Depends(get_db)):
    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()
    # Join with students for names
    result = []
    for log in logs:
        result.append({
            "student_id": log.student_id,
            "name": log.student.full_name,
            "status": log.status,
            "time": log.timestamp
        })
    return result
