from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import deps
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Update own user.
    """
    if user_in.password:
        current_user.hashed_password = deps.security.get_password_hash(user_in.password)
    if user_in.full_name:
        current_user.full_name = user_in.full_name
    if user_in.email:
        current_user.email = user_in.email
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/guests")
async def get_guests():
    return {"message": "Get Guests"}

@router.post("/guests")
async def add_guest():
    return {"message": "Add Guest"}

@router.put("/guests/{guestId}")
async def update_guest(guestId: int):
    return {"message": f"Update Guest {guestId}"}

@router.delete("/guests/{guestId}")
async def remove_guest(guestId: int):
    return {"message": f"Remove Guest {guestId}"}

@router.get("/myBookings")
async def get_my_bookings():
    return {"message": "Get My Bookings"}
