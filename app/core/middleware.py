"""
Tenant Isolation Middleware
Ensures all database queries are scoped to the current user's institution.
"""

from fastapi import HTTPException
from typing import Optional
from app.db.models import User, UserRole


class TenantContext:
    """Holds the current tenant (institution) context for a request"""

    def __init__(
        self, institution_id: Optional[int] = None, is_super_admin: bool = False
    ):
        self.institution_id = institution_id
        self.is_super_admin = is_super_admin

    def can_access_institution(self, target_institution_id: int) -> bool:
        """Check if current user can access a specific institution"""
        if self.is_super_admin:
            return True
        return self.institution_id == target_institution_id


def get_tenant_context(user: Optional[User]) -> TenantContext:
    """Extract tenant context from authenticated user"""
    if not user:
        return TenantContext()

    is_super = user.role == UserRole.SUPER_ADMIN.value
    return TenantContext(institution_id=user.institution_id, is_super_admin=is_super)


def require_institution_access(user: User, institution_id: int):
    """Middleware helper to verify user can access an institution"""
    if user.role == UserRole.SUPER_ADMIN.value:
        return True

    if user.institution_id != institution_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You don't belong to this institution",
        )
    return True


def require_role(user: User, allowed_roles: list):
    """Middleware helper to verify user has required role"""
    if user.role not in [r.value if hasattr(r, "value") else r for r in allowed_roles]:
        raise HTTPException(
            status_code=403, detail=f"Access denied: Required roles: {allowed_roles}"
        )
    return True


def require_super_admin(user: User):
    """Require super admin role"""
    return require_role(user, [UserRole.SUPER_ADMIN])


def require_admin_or_above(user: User):
    """Require admin or super admin role"""
    return require_role(user, [UserRole.SUPER_ADMIN, UserRole.ADMIN])


def require_teacher_or_above(user: User):
    """Require teacher, admin, or super admin role"""
    return require_role(user, [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.TEACHER])
