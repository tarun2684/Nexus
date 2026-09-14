"""Authentication endpoints for fastapi-users."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.auth import (
    get_fastapi_users,
    UserCreate,
    UserRead,
    UserUpdate,
    get_current_active_user,
)
from app.models.user import User

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    fastapi_users_dep=Depends(get_fastapi_users),
):
    """Register a new user.
    
    In Sprint 5 with invites enabled, this will require a valid invite code.
    For now, registration is open for testing.
    """
    # Use the built-in register method from fastapi-users
    return await fastapi_users_dep.register(user_create)


class ProfileUpdate(BaseModel):
    """Fields users can update in their profile."""
    display_name: str | None = None
    avatar: str | None = None


@router.get("/me/profile", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's profile."""
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar=current_user.avatar,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.patch("/me/profile", response_model=UserRead)
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    fastapi_users_dep=Depends(get_fastapi_users),
):
    """Update current user's profile."""
    # Build update dict with only provided fields
    update_data = {}
    if profile_update.display_name is not None:
        update_data["display_name"] = profile_update.display_name
    if profile_update.avatar is not None:
        update_data["avatar"] = profile_update.avatar
    
    # Use fastapi-users update method
    updated_user = await fastapi_users_dep.update_user(
        UserUpdate(**update_data),
        current_user,
    )
    
    return UserRead(
        id=updated_user.id,
        email=updated_user.email,
        display_name=updated_user.display_name,
        avatar=updated_user.avatar,
        role=updated_user.role,
        is_active=updated_user.is_active,
    )
