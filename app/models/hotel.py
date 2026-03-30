from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price_per_night = Column(Float, nullable=False)
    capacity = Column(Integer, default=2)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    hotel = relationship("Hotel", back_populates="rooms")
    
    # Relationships for booking system
    bookings = relationship("Booking", back_populates="room")
    inventory = relationship("RoomInventory", back_populates="room", cascade="all, delete-orphan")
