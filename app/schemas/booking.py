from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import date, datetime
from enum import Enum


class BookingStatus(str, Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


# ============ Guest Schemas ============

class GuestBase(BaseModel):
    """Base guest schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=120)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, +, -, and spaces')
        return v


class GuestCreate(GuestBase):
    """Schema for creating a saved guest"""
    pass


class GuestUpdate(BaseModel):
    """Schema for updating a saved guest"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=120)


class GuestResponse(GuestBase):
    """Schema for guest response"""
    id: int
    is_primary_guest: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GuestInBooking(GuestBase):
    """Schema for guest within a booking"""
    is_primary_guest: bool = False


# ============ Payment Schemas ============

class PaymentBase(BaseModel):
    """Base payment schema"""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)


class PaymentCreate(PaymentBase):
    """Schema for creating a payment"""
    payment_method: Optional[str] = None


class PaymentIntentResponse(BaseModel):
    """Schema for Stripe payment intent response"""
    client_secret: str
    payment_intent_id: str


class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    id: int
    booking_id: int
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str]
    payment_method: Optional[str]
    paid_at: Optional[datetime]
    refunded_at: Optional[datetime]
    refund_amount: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Booking Schemas ============

class BookingBase(BaseModel):
    """Base booking schema"""
    room_id: int = Field(..., gt=0)
    check_in: date
    check_out: date
    num_guests: int = Field(..., gt=0, le=50)
    special_requests: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('check_out')
    @classmethod
    def validate_dates(cls, v, info):
        check_in = info.data.get('check_in')
        if check_in and v <= check_in:
            raise ValueError('Check-out must be after check-in')
        if check_in and (v - check_in).days > 30:
            raise ValueError('Maximum stay is 30 nights')
        return v
    
    @field_validator('check_in')
    @classmethod
    def validate_check_in(cls, v):
        if v < date.today():
            raise ValueError('Check-in date must be in the future')
        return v


class BookingInit(BookingBase):
    """Schema for initializing a booking"""
    pass


class BookingCreate(BookingBase):
    """Schema for creating a booking (internal)"""
    user_id: int
    total_price: float
    status: BookingStatus = BookingStatus.PENDING


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = Field(None, max_length=1000)
    cancellation_reason: Optional[str] = Field(None, max_length=500)


class BookingAddGuests(BaseModel):
    """Schema for adding guests to a booking"""
    guests: List[GuestInBooking] = Field(..., min_length=1)
    
    @field_validator('guests')
    @classmethod
    def validate_primary_guest(cls, v):
        primary_count = sum(1 for g in v if g.is_primary_guest)
        if primary_count != 1:
            raise ValueError('Exactly one guest must be marked as primary')
        return v


class BookingCancellation(BaseModel):
    """Schema for cancelling a booking"""
    reason: Optional[str] = Field(None, max_length=500)


class BookingResponse(BookingBase):
    """Schema for booking response"""
    id: int
    user_id: int
    total_price: float
    status: BookingStatus
    cancellation_reason: Optional[str]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    guests: List[GuestResponse] = []
    payment: Optional[PaymentResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class BookingListItem(BaseModel):
    """Schema for booking list item (summary)"""
    id: int
    room_id: int
    check_in: date
    check_out: date
    num_guests: int
    total_price: float
    status: BookingStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Inventory Schemas ============

class InventoryBase(BaseModel):
    """Base inventory schema"""
    date: date
    available_count: int = Field(..., ge=0)
    total_count: int = Field(..., gt=0)
    price_override: Optional[float] = Field(None, gt=0)
    
    @field_validator('available_count')
    @classmethod
    def validate_availability(cls, v, info):
        total = info.data.get('total_count')
        if total and v > total:
            raise ValueError('Available count cannot exceed total count')
        return v


class InventoryUpdate(BaseModel):
    """Schema for updating inventory"""
    available_count: Optional[int] = Field(None, ge=0)
    price_override: Optional[float] = Field(None, gt=0)


class InventoryResponse(InventoryBase):
    """Schema for inventory response"""
    id: int
    room_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InventoryDateRange(BaseModel):
    """Schema for querying inventory date range"""
    start_date: date
    end_date: date
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        start = info.data.get('start_date')
        if start and v < start:
            raise ValueError('End date must be after start date')
        if start and (v - start).days > 365:
            raise ValueError('Maximum date range is 365 days')
        return v


# ============ Report Schemas ============

class BookingReportItem(BaseModel):
    """Schema for booking report item"""
    booking_id: int
    room_name: str
    guest_name: str
    check_in: date
    check_out: date
    total_price: float
    status: BookingStatus
    created_at: datetime


class HotelBookingReport(BaseModel):
    """Schema for hotel booking report"""
    hotel_id: int
    hotel_name: str
    total_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    total_revenue: float
    bookings: List[BookingReportItem]
