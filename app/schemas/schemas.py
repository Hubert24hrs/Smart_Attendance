from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StudentBase(BaseModel):
    full_name: str
    student_id: str

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

class AttendanceRecord(BaseModel):
    student_id: int
    student_name: str
    status: str
    timestamp: datetime
