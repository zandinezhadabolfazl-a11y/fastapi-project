# app/auth/permissions.py
from fastapi import HTTPException, status
from app.schemas.user import UserRole
from app.models import User

def require_admin(user: User):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission (Admin only)"
        )

def require_owner_or_admin(user: User, resource_owner_id: int):
    if user.role != UserRole.ADMIN and user.id != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own resources"
        )
