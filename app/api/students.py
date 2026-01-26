from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Student, FaceEmbedding
from app.services.face_logic import FaceLogic
from app.schemas.schemas import StudentResponse
import pickle

router = APIRouter()

@router.post("/enroll", response_model=StudentResponse)
async def enroll_student(
    full_name: str = Form(...),
    student_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Enroll a student by uploading multiple face images.
    System extracts embeddings and stores them.
    """
    # 1. Create Student
    existing = db.query(Student).filter(Student.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    new_student = Student(full_name=full_name, student_id=student_id)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # 2. Process Images
    valid_embeddings = 0
    for file in files:
        content = await file.read()
        encodings = FaceLogic.process_image(content)
        
        if len(encodings) == 1: # Strict: Only assume correct face if exactly 1 face found
            # Store embedding
            emb_bytes = pickle.dumps(encodings[0])
            db_emb = FaceEmbedding(student_id=new_student.id, embedding_bytes=emb_bytes)
            db.add(db_emb)
            valid_embeddings += 1
        elif len(encodings) > 1:
            print(f"Warning: Multiple faces in enrollment image for {full_name}. Skipping.")
        else:
            print(f"Warning: No faces in enrollment image for {full_name}. Skipping.")
    
    if valid_embeddings == 0:
        db.delete(new_student)
        db.commit()
        raise HTTPException(status_code=400, detail="No valid face embeddings found in uploaded images.")
    
    db.commit()
    return new_student

@router.get("/", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()
