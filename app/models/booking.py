from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class BookingStatus(str, enum.Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Booking(Base):
    """Booking model for hotel room reservations"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    
    check_in = Column(Date, nullable=False, index=True)
    check_out = Column(Date, nullable=False, index=True)
    
    total_price = Column(Float, nullable=False)
    num_guests = Column(Integer, nullable=False)
    
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    
    special_requests = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    guests = relationship("Guest", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")


class Guest(Base):
    """Guest model for booking participants"""
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # For saved guests
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    
    is_primary_guest = Column(Integer, default=0, nullable=False)  # 0=False, 1=True (SQLite doesn't have Boolean)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="guests")
    user = relationship("User", back_populates="saved_guests")


class Payment(Base):
    """Payment model for booking transactions"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, unique=True, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    
    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True, index=True)
    payment_method = Column(String(50), nullable=True)
    
    paid_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    refund_amount = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="payment")


class RoomInventory(Base):
    """Room inventory model for availability tracking"""
    __tablename__ = "room_inventory"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    
    date = Column(Date, nullable=False, index=True)
    available_count = Column(Integer, nullable=False)
    total_count = Column(Integer, nullable=False)
    
    price_override = Column(Float, nullable=True)  # Override room base price for specific dates
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    room = relationship("Room", back_populates="inventory")
    
    # Composite unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
