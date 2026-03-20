from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.hotel import Hotel, Room
from app.schemas.hotel import HotelList, HotelResponse

router = APIRouter()

@router.get("/search", response_model=List[HotelList])
async def search_hotels(
    location: Optional[str] = Query(None, min_length=3),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Search for hotels. If location is provided, filters by location.
    Otherwise returns all active hotels.
    """
    query = select(Hotel).where(Hotel.is_active == True)
    if location:
        query = query.filter(Hotel.location.ilike(f"%{location}%"))
    
    result = await db.execute(query)
    hotels = result.scalars().all()
    return hotels

@router.get("/{hotelId}/info", response_model=HotelResponse)
async def get_hotel_info(
    hotelId: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get detailed information about a specific hotel, including its rooms.
    """
    # Use selectinload to eagerly load the 'rooms' relationship
    query = select(Hotel).options(selectinload(Hotel.rooms)).filter(Hotel.id == hotelId)
    result = await db.execute(query)
    hotel = result.scalars().first()
    
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
        
    return hotel
