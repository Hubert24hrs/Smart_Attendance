"""
Institution Management API - SuperAdmin only
/api/v1/institutions/
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.db.models import Institution, User, UserRole, SubscriptionTier
from app.api.auth import get_current_user
from app.core.middleware import require_super_admin
from app.core.security import get_password_hash

router = APIRouter()

# =============================================================================
# SCHEMAS
# =============================================================================
class InstitutionCreate(BaseModel):
    name: str
    slug: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_tier: str = SubscriptionTier.FREE.value

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_active: Optional[bool] = None
    max_students: Optional[int] = None

class InstitutionResponse(BaseModel):
    id: int
    name: str
    slug: str
    email: Optional[str]
    subscription_tier: str
    max_students: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/", response_model=List[InstitutionResponse])
def list_institutions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all institutions (SuperAdmin only)"""
    require_super_admin(current_user)
    return db.query(Institution).all()

@router.post("/", response_model=InstitutionResponse)
def create_institution(
    data: InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new institution (SuperAdmin only)"""
    require_super_admin(current_user)
    
    # Check slug uniqueness
    existing = db.query(Institution).filter(Institution.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    institution = Institution(
        name=data.name,
        slug=data.slug,
        email=data.email,
        phone=data.phone,
        address=data.address,
        subscription_tier=data.subscription_tier,
        max_students=50 if data.subscription_tier == SubscriptionTier.FREE.value else 500
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)
    return institution

@router.get("/{institution_id}", response_model=InstitutionResponse)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get institution details"""
    # Allow super admin or institution members
    institution = db.get(Institution, institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    if current_user.role != UserRole.SUPER_ADMIN.value:
        if current_user.institution_id != institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return institution

@router.patch("/{institution_id}", response_model=InstitutionResponse)
def update_institution(
    institution_id: int,
    data: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update institution (SuperAdmin only)"""
    require_super_admin(current_user)
    
    institution = db.get(Institution, institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(institution, key, value)
    
    db.commit()
    db.refresh(institution)
    return institution

@router.delete("/{institution_id}")
def delete_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete institution (SuperAdmin only) - Soft delete"""
    require_super_admin(current_user)
    
    institution = db.get(Institution, institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    institution.is_active = False
    db.commit()
    return {"message": "Institution deactivated"}

@router.post("/{institution_id}/admin")
def create_institution_admin(
    institution_id: int,
    data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an admin user for an institution (SuperAdmin only)"""
    require_super_admin(current_user)
    
    institution = db.get(Institution, institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Check username uniqueness
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    admin = User(
        institution_id=institution_id,
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=UserRole.ADMIN.value
    )
    db.add(admin)
    db.commit()
    
    return {"message": f"Admin '{data.username}' created for {institution.name}"}

@router.get("/{institution_id}/stats")
def get_institution_stats(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get institution statistics"""
    from app.db.models import Student, Course, ClassSession
    
    # Access check
    if current_user.role != UserRole.SUPER_ADMIN.value:
        if current_user.institution_id != institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    institution = db.get(Institution, institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    total_students = db.query(Student).filter(Student.institution_id == institution_id).count()
    total_courses = db.query(Course).filter(Course.institution_id == institution_id).count()
    total_teachers = db.query(User).filter(
        User.institution_id == institution_id,
        User.role == UserRole.TEACHER.value
    ).count()
    
    return {
        "institution": institution.name,
        "total_students": total_students,
        "total_courses": total_courses,
        "total_teachers": total_teachers,
        "subscription_tier": institution.subscription_tier,
        "max_students": institution.max_students
    }
