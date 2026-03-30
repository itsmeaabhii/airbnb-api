from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.booking import Guest
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.booking import GuestCreate, GuestUpdate, GuestResponse, BookingListItem
from app.services.booking_service import BookingService
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user


@router.patch("/profile", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    # Update fields
    if user_update.email is not None:
        # Check if email already exists
        result = await db.execute(
            select(User).filter(User.email == user_update.email, User.id != current_user.id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/guests", response_model=List[GuestResponse])
async def get_saved_guests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of saved guests for quick booking
    
    Returns all guests that the user has saved for future bookings
    """
    result = await db.execute(
        select(Guest)
        .filter(Guest.user_id == current_user.id, Guest.booking_id == None)
        .order_by(Guest.created_at.desc())
    )
    guests = result.scalars().all()
    
    # Convert is_primary_guest from int to bool
    guests_list = []
    for guest in guests:
        guest_dict = {
            "id": guest.id,
            "first_name": guest.first_name,
            "last_name": guest.last_name,
            "email": guest.email,
            "phone": guest.phone,
            "age": guest.age,
            "is_primary_guest": bool(guest.is_primary_guest),
            "created_at": guest.created_at
        }
        guests_list.append(GuestResponse(**guest_dict))
    
    return guests_list


@router.post("/guests", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
async def add_saved_guest(
    guest_data: GuestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new saved guest
    
    Save guest information for quick access in future bookings
    """
    guest = Guest(
        user_id=current_user.id,
        first_name=guest_data.first_name,
        last_name=guest_data.last_name,
        email=guest_data.email,
        phone=guest_data.phone,
        age=guest_data.age,
        is_primary_guest=0
    )
    
    db.add(guest)
    await db.commit()
    await db.refresh(guest)
    
    # Convert to response
    guest_dict = {
        "id": guest.id,
        "first_name": guest.first_name,
        "last_name": guest.last_name,
        "email": guest.email,
        "phone": guest.phone,
        "age": guest.age,
        "is_primary_guest": False,
        "created_at": guest.created_at
    }
    return GuestResponse(**guest_dict)


@router.put("/guests/{guestId}", response_model=GuestResponse)
async def update_saved_guest(
    guestId: int,
    guest_update: GuestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a saved guest
    
    Update guest information. Only saved guests (not attached to bookings) can be updated.
    """
    result = await db.execute(
        select(Guest).filter(
            Guest.id == guestId,
            Guest.user_id == current_user.id,
            Guest.booking_id == None
        )
    )
    guest = result.scalars().first()
    
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved guest not found"
        )
    
    # Update fields
    if guest_update.first_name is not None:
        guest.first_name = guest_update.first_name
    if guest_update.last_name is not None:
        guest.last_name = guest_update.last_name
    if guest_update.email is not None:
        guest.email = guest_update.email
    if guest_update.phone is not None:
        guest.phone = guest_update.phone
    if guest_update.age is not None:
        guest.age = guest_update.age
    
    await db.commit()
    await db.refresh(guest)
    
    # Convert to response
    guest_dict = {
        "id": guest.id,
        "first_name": guest.first_name,
        "last_name": guest.last_name,
        "email": guest.email,
        "phone": guest.phone,
        "age": guest.age,
        "is_primary_guest": False,
        "created_at": guest.created_at
    }
    return GuestResponse(**guest_dict)


@router.delete("/guests/{guestId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_guest(
    guestId: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a saved guest
    
    Remove a saved guest from your profile. Cannot delete guests attached to bookings.
    """
    result = await db.execute(
        select(Guest).filter(
            Guest.id == guestId,
            Guest.user_id == current_user.id,
            Guest.booking_id == None
        )
    )
    guest = result.scalars().first()
    
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved guest not found"
        )
    
    await db.delete(guest)
    await db.commit()
    return None


@router.get("/myBookings", response_model=List[BookingListItem])
async def get_my_bookings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's bookings
    
    Returns a list of all bookings made by the current user, ordered by most recent first
    """
    bookings = await BookingService.get_user_bookings(db, current_user.id, skip, limit)
    return bookings
