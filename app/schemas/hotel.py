from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# Room Schemas
class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_per_night: float
    capacity: Optional[int] = 2
    image_url: Optional[str] = None
    is_available: Optional[bool] = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_night: Optional[float] = None
    capacity: Optional[int] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

class RoomResponse(RoomBase):
    id: int
    hotel_id: int

    model_config = ConfigDict(from_attributes=True)

# Hotel Schemas
class HotelBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = False

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class HotelResponse(HotelBase):
    id: int
    rooms: List[RoomResponse] = []

    model_config = ConfigDict(from_attributes=True)

class HotelList(BaseModel):
    id: int
    name: str
    location: str
    description: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
