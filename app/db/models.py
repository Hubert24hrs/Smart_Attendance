from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="teacher") # teacher, admin

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    student_id = Column(String, unique=True, index=True) 
    
    # Relationships
    embeddings = relationship("FaceEmbedding", back_populates="student")
    attendance_records = relationship("AttendanceLog", back_populates="student")

class FaceEmbedding(Base):
    """Stores the 128-d face encoding vector as bytes"""
    __tablename__ = "face_embeddings"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    embedding_bytes = Column(LargeBinary) # numpy array tobytes()
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="embeddings")

class ClassSession(Base):
    """Represents a single class session initiated by a teacher"""
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    course_name = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    attendance_logs = relationship("AttendanceLog", back_populates="session")

class AttendanceLog(Base):
    """Records the final status of a student for a session"""
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    status = Column(String, default="PRESENT") # PRESENT, ABSENT
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    
    session = relationship("ClassSession", back_populates="attendance_logs")
    student = relationship("Student", back_populates="attendance_records")

class RawDetection(Base):
    """Frame-by-frame detection log for N-frame consistency rule"""
    __tablename__ = "raw_detections"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    frame_number = Column(Integer)
    distance = Column(Float)
    is_static = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    """Course/Class that students are enrolled in"""
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # e.g., "MATH101"
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("User")

# Many-to-many: StudentCourse
class StudentCourse(Base):
    """Enrollment: Links students to courses"""
    __tablename__ = "student_courses"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)


