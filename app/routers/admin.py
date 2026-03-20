from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app import deps
from app.models.hotel import Hotel, Room
from app.models.user import User
from app.schemas.hotel import (
    HotelCreate, HotelResponse, HotelUpdate, HotelList,
    RoomCreate, RoomResponse, RoomUpdate
)

router = APIRouter()

# Admin check dependency
async def get_current_superuser(current_user: User = Depends(deps.get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user

# --- Hotel Management ---

@router.get("/hotels", response_model=List[HotelList])
async def get_admin_hotels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Get all hotels (admin only).
    """
    result = await db.execute(select(Hotel))
    return result.scalars().all()

@router.post("/hotels", response_model=HotelResponse)
async def create_hotel(
    hotel_in: HotelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Create a new hotel.
    """
    hotel = Hotel(
        name=hotel_in.name,
        location=hotel_in.location,
        description=hotel_in.description,
        image_url=hotel_in.image_url,
        is_active=hotel_in.is_active
    )
    db.add(hotel)
    await db.commit()
    await db.refresh(hotel)
    
    # Reload with eager loading to satisfy response model
    result = await db.execute(select(Hotel).options(selectinload(Hotel.rooms)).filter(Hotel.id == hotel.id))
    hotel = result.scalars().first()
    
    return hotel

@router.get("/hotels/{hotelId}", response_model=HotelResponse)
async def get_hotel(
    hotelId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Get hotel by ID.
    """
    query = select(Hotel).options(selectinload(Hotel.rooms)).filter(Hotel.id == hotelId)
    result = await db.execute(query)
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.put("/hotels/{hotelId}", response_model=HotelResponse)
async def update_hotel(
    hotelId: int,
    hotel_in: HotelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Update hotel details.
    """
    query = select(Hotel).filter(Hotel.id == hotelId)
    result = await db.execute(query)
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    if hotel_in.name is not None: hotel.name = hotel_in.name
    if hotel_in.location is not None: hotel.location = hotel_in.location
    if hotel_in.description is not None: hotel.description = hotel_in.description
    if hotel_in.image_url is not None: hotel.image_url = hotel_in.image_url
    if hotel_in.is_active is not None: hotel.is_active = hotel_in.is_active
    
    await db.commit()
    await db.refresh(hotel)
    
    # Reload with eager loading
    result = await db.execute(select(Hotel).options(selectinload(Hotel.rooms)).filter(Hotel.id == hotel.id))
    hotel = result.scalars().first()
    
    return hotel

@router.delete("/hotels/{hotelId}")
async def delete_hotel(
    hotelId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Delete a hotel.
    """
    query = select(Hotel).filter(Hotel.id == hotelId)
    result = await db.execute(query)
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    await db.delete(hotel)
    await db.commit()
    return {"message": "Hotel deleted successfully"}

@router.patch("/hotels/{hotelId}/activate")
async def activate_hotel(
    hotelId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Activate a hotel.
    """
    query = select(Hotel).filter(Hotel.id == hotelId)
    result = await db.execute(query)
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    hotel.is_active = True
    await db.commit()
    return {"message": "Hotel activated"}

# --- Room Management ---

@router.get("/hotels/{hotelId}/rooms", response_model=List[RoomResponse])
async def get_rooms(
    hotelId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Get all rooms for a hotel.
    """
    query = select(Room).filter(Room.hotel_id == hotelId)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/hotels/{hotelId}/rooms", response_model=RoomResponse)
async def create_room(
    hotelId: int,
    room_in: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Create a room for a hotel.
    """
    # Verify hotel exists
    result = await db.execute(select(Hotel).filter(Hotel.id == hotelId))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Hotel not found")

    room = Room(
        name=room_in.name,
        description=room_in.description,
        price_per_night=room_in.price_per_night,
        capacity=room_in.capacity,
        image_url=room_in.image_url,
        is_available=room_in.is_available,
        hotel_id=hotelId
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room

@router.get("/hotels/{hotelId}/rooms/{roomId}", response_model=RoomResponse)
async def get_room(
    hotelId: int, 
    roomId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Get room details.
    """
    query = select(Room).filter(Room.id == roomId, Room.hotel_id == hotelId)
    result = await db.execute(query)
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/hotels/{hotelId}/rooms/{roomId}", response_model=RoomResponse)
async def update_room(
    hotelId: int, 
    roomId: int,
    room_in: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Update a room.
    """
    query = select(Room).filter(Room.id == roomId, Room.hotel_id == hotelId)
    result = await db.execute(query)
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room_in.name is not None: room.name = room_in.name
    if room_in.description is not None: room.description = room_in.description
    if room_in.price_per_night is not None: room.price_per_night = room_in.price_per_night
    if room_in.capacity is not None: room.capacity = room_in.capacity
    if room_in.image_url is not None: room.image_url = room_in.image_url
    if room_in.is_available is not None: room.is_available = room_in.is_available
    
    await db.commit()
    await db.refresh(room)
    return room

@router.delete("/hotels/{hotelId}/rooms/{roomId}")
async def delete_room(
    hotelId: int, 
    roomId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Delete a room.
    """
    query = select(Room).filter(Room.id == roomId, Room.hotel_id == hotelId)
    result = await db.execute(query)
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    await db.delete(room)
    await db.commit()
    return {"message": "Room deleted successfully"}
