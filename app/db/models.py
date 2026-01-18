from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, LargeBinary, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"  # Platform owner - manages all institutions
    ADMIN = "admin"              # Institution admin - manages their school
    TEACHER = "teacher"          # Teacher - takes attendance

class SubscriptionTier(str, Enum):
    FREE = "free"           # Up to 50 students
    BASIC = "basic"         # Up to 500 students
    PRO = "pro"             # Up to 2000 students
    ENTERPRISE = "enterprise"  # Unlimited

# =============================================================================
# INSTITUTION (Multi-Tenant Core)
# =============================================================================
class Institution(Base):
    """Each school/college/institution is a tenant"""
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)  # URL-friendly identifier
    email = Column(String)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    
    # Subscription
    subscription_tier = Column(String, default=SubscriptionTier.FREE.value)
    subscription_expires = Column(DateTime, nullable=True)
    max_students = Column(Integer, default=50)
    
    # Settings (JSON for flexibility)
    settings = Column(JSON, default={})
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="institution")
    students = relationship("Student", back_populates="institution")
    courses = relationship("Course", back_populates="institution")

# =============================================================================
# USER (Multi-Tenant)
# =============================================================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)  # Null for super_admin
    
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.TEACHER.value)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    institution = relationship("Institution", back_populates="users")

# =============================================================================
# STUDENT (Multi-Tenant)
# =============================================================================
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    
    full_name = Column(String)
    student_id = Column(String, index=True)  # Now unique per institution, not global
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="students")
    embeddings = relationship("FaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceLog", back_populates="student")
    enrollments = relationship("StudentCourse", back_populates="student")

# =============================================================================
# FACE EMBEDDING
# =============================================================================
class FaceEmbedding(Base):
    """Stores the 128-d face encoding vector as bytes"""
    __tablename__ = "face_embeddings"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    embedding_bytes = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="embeddings")

# =============================================================================
# COURSE (Multi-Tenant)
# =============================================================================
class Course(Base):
    """Course/Class that students are enrolled in"""
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    
    code = Column(String, index=True)  # e.g., "MATH101" - unique per institution
    name = Column(String)
    description = Column(Text, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    institution = relationship("Institution", back_populates="courses")
    teacher = relationship("User")
    sessions = relationship("ClassSession", back_populates="course")
    enrollments = relationship("StudentCourse", back_populates="course")

# =============================================================================
# STUDENT COURSE ENROLLMENT
# =============================================================================
class StudentCourse(Base):
    """Many-to-Many: Links students to courses"""
    __tablename__ = "student_courses"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

# =============================================================================
# CLASS SESSION (Multi-Tenant via Course)
# =============================================================================
class ClassSession(Base):
    """Represents a single attendance session initiated by a teacher"""
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    course_name = Column(String)  # Kept for backward compatibility
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Location verification (optional)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    course = relationship("Course", back_populates="sessions")
    attendance_logs = relationship("AttendanceLog", back_populates="session", cascade="all, delete-orphan")
    raw_detections = relationship("RawDetection", back_populates="session", cascade="all, delete-orphan")

# =============================================================================
# ATTENDANCE LOG
# =============================================================================
class AttendanceLog(Base):
    """Records the final status of a student for a session"""
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id"))
    
    status = Column(String, default="PRESENT")  # PRESENT, ABSENT, LATE
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float, nullable=True)
    
    session = relationship("ClassSession", back_populates="attendance_logs")
    student = relationship("Student", back_populates="attendance_records")

# =============================================================================
# RAW DETECTION (Frame-by-frame for N-frame rule)
# =============================================================================
class RawDetection(Base):
    """Frame-by-frame detection log for N-frame consistency rule"""
    __tablename__ = "raw_detections"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id"))
    
    frame_number = Column(Integer)
    distance = Column(Float)
    is_static = Column(Boolean, default=False)  # Liveness flag
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ClassSession", back_populates="raw_detections")

# =============================================================================
# ATTENDANCE STATS (Analytics - Daily Aggregates)
# =============================================================================
class AttendanceStats(Base):
    """Daily attendance statistics per institution/course"""
    __tablename__ = "attendance_stats"
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    date = Column(DateTime)
    total_students = Column(Integer, default=0)
    total_present = Column(Integer, default=0)
    total_absent = Column(Integer, default=0)
    attendance_rate = Column(Float, default=0.0)  # Percentage
    
    created_at = Column(DateTime, default=datetime.utcnow)
