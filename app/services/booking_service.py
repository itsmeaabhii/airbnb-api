from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
import logging

from app.models.booking import Booking, Guest, Payment, RoomInventory, BookingStatus, PaymentStatus
from app.models.hotel import Room
from app.schemas.booking import BookingInit, BookingAddGuests
from app.core.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger("airbnb_api")


class BookingService:
    """Service for booking business logic"""
    
    @staticmethod
    async def check_availability(
        db: AsyncSession,
        room_id: int,
        check_in: date,
        check_out: date,
        num_guests: int
    ) -> Tuple[bool, Optional[str], float]:
        """
        Check if room is available for given dates
        Returns: (is_available, error_message, total_price)
        """
        # Get room details
        result = await db.execute(select(Room).filter(Room.id == room_id))
        room = result.scalars().first()
        
        if not room:
            return False, "Room not found", 0.0
        
        if not room.is_available:
            return False, "Room is not available for booking", 0.0
        
        if num_guests > room.capacity:
            return False, f"Room capacity is {room.capacity}, but {num_guests} guests requested", 0.0
        
        # Check for overlapping bookings
        num_nights = (check_out - check_in).days
        dates_to_check = [check_in + timedelta(days=i) for i in range(num_nights)]
        
        # Count existing bookings for each date
        for check_date in dates_to_check:
            query = select(func.count(Booking.id)).filter(
                and_(
                    Booking.room_id == room_id,
                    Booking.check_in <= check_date,
                    Booking.check_out > check_date,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                )
            )
            result = await db.execute(query)
            booking_count = result.scalar()
            
            # For simplicity, assuming 1 room per room_id
            # In a real system, you'd check inventory table
            if booking_count > 0:
                return False, f"Room is not available on {check_date}", 0.0
        
        # Calculate total price
        total_price = room.price_per_night * num_nights
        
        return True, None, total_price
    
    @staticmethod
    async def initialize_booking(
        db: AsyncSession,
        user_id: int,
        booking_data: BookingInit
    ) -> Booking:
        """Initialize a new booking"""
        
        # Check availability
        is_available, error, total_price = await BookingService.check_availability(
            db,
            booking_data.room_id,
            booking_data.check_in,
            booking_data.check_out,
            booking_data.num_guests
        )
        
        if not is_available:
            raise BadRequestException(error)
        
        # Create booking
        booking = Booking(
            user_id=user_id,
            room_id=booking_data.room_id,
            check_in=booking_data.check_in,
            check_out=booking_data.check_out,
            num_guests=booking_data.num_guests,
            total_price=total_price,
            special_requests=booking_data.special_requests,
            status=BookingStatus.PENDING
        )
        
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        
        logger.info(f"Booking {booking.id} initialized for user {user_id}")
        return booking
    
    @staticmethod
    async def add_guests_to_booking(
        db: AsyncSession,
        booking_id: int,
        user_id: int,
        guests_data: BookingAddGuests
    ) -> Booking:
        """Add guests to a booking"""
        
        # Get booking
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.guests))
            .filter(Booking.id == booking_id)
        )
        booking = result.scalars().first()
        
        if not booking:
            raise NotFoundException("Booking not found")
        
        if booking.user_id != user_id:
            raise BadRequestException("Not authorized to modify this booking")
        
        if booking.status not in [BookingStatus.PENDING]:
            raise BadRequestException("Cannot add guests to a non-pending booking")
        
        # Validate guest count
        if len(guests_data.guests) != booking.num_guests:
            raise BadRequestException(
                f"Number of guests ({len(guests_data.guests)}) does not match booking ({booking.num_guests})"
            )
        
        # Remove existing guests if any
        for guest in booking.guests:
            await db.delete(guest)
        
        # Add new guests
        for guest_data in guests_data.guests:
            guest = Guest(
                booking_id=booking_id,
                first_name=guest_data.first_name,
                last_name=guest_data.last_name,
                email=guest_data.email,
                phone=guest_data.phone,
                age=guest_data.age,
                is_primary_guest=1 if guest_data.is_primary_guest else 0
            )
            db.add(guest)
        
        await db.commit()
        await db.refresh(booking)
        
        logger.info(f"Added {len(guests_data.guests)} guests to booking {booking_id}")
        return booking
    
    @staticmethod
    async def calculate_cancellation_refund(booking: Booking) -> float:
        """Calculate refund amount based on cancellation policy"""
        days_until_checkin = (booking.check_in - date.today()).days
        
        if days_until_checkin > 7:
            return booking.total_price  # 100% refund
        elif days_until_checkin >= 2:
            return booking.total_price * 0.5  # 50% refund
        else:
            return 0.0  # No refund
    
    @staticmethod
    async def cancel_booking(
        db: AsyncSession,
        booking_id: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> Booking:
        """Cancel a booking"""
        
        # Get booking with payment
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.payment))
            .filter(Booking.id == booking_id)
        )
        booking = result.scalars().first()
        
        if not booking:
            raise NotFoundException("Booking not found")
        
        if booking.user_id != user_id:
            raise BadRequestException("Not authorized to cancel this booking")
        
        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestException("Booking is already cancelled")
        
        if booking.status == BookingStatus.COMPLETED:
            raise BadRequestException("Cannot cancel a completed booking")
        
        # Calculate refund
        refund_amount = await BookingService.calculate_cancellation_refund(booking)
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = reason
        booking.cancelled_at = datetime.utcnow()
        
        # Update payment if exists and was successful
        if booking.payment and booking.payment.status == PaymentStatus.SUCCEEDED:
            booking.payment.status = PaymentStatus.REFUNDED
            booking.payment.refunded_at = datetime.utcnow()
            booking.payment.refund_amount = refund_amount
        
        await db.commit()
        await db.refresh(booking)
        
        logger.info(f"Booking {booking_id} cancelled with refund amount {refund_amount}")
        return booking
    
    @staticmethod
    async def get_user_bookings(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Booking]:
        """Get all bookings for a user"""
        
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.guests), selectinload(Booking.payment))
            .filter(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_booking_by_id(
        db: AsyncSession,
        booking_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Booking]:
        """Get booking by ID with optional user validation"""
        
        query = (
            select(Booking)
            .options(selectinload(Booking.guests), selectinload(Booking.payment))
            .filter(Booking.id == booking_id)
        )
        
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        
        result = await db.execute(query)
        return result.scalars().first()
