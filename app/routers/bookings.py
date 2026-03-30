from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.booking import (
    BookingInit,
    BookingResponse,
    BookingAddGuests,
    BookingCancellation,
    BookingListItem,
    PaymentCreate,
    PaymentIntentResponse
)
from app.services.booking_service import BookingService
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()
logger = logging.getLogger("airbnb_api")


@router.post("/init", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def initialize_booking(
    booking_data: BookingInit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a new booking
    
    - **room_id**: ID of the room to book
    - **check_in**: Check-in date (must be future date)
    - **check_out**: Check-out date (must be after check-in)
    - **num_guests**: Number of guests (must not exceed room capacity)
    - **special_requests**: Optional special requests
    
    Returns the created booking with PENDING status
    """
    try:
        booking = await BookingService.initialize_booking(db, current_user.id, booking_data)
        logger.info(f"User {current_user.id} initialized booking {booking.id}")
        return booking
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{bookingId}/status", response_model=BookingResponse)
async def get_booking_status(
    bookingId: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get booking status and details
    
    Returns complete booking information including guests and payment status
    """
    booking = await BookingService.get_booking_by_id(db, bookingId, current_user.id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking


@router.post("/{bookingId}/addGuests", response_model=BookingResponse)
async def add_guests_to_booking(
    bookingId: int,
    guests_data: BookingAddGuests,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add guests to a booking
    
    - **guests**: List of guests (must match num_guests in booking)
    - Exactly one guest must be marked as primary
    - All guests must have valid contact information
    
    Returns the updated booking with guest information
    """
    try:
        booking = await BookingService.add_guests_to_booking(
            db, bookingId, current_user.id, guests_data
        )
        logger.info(f"Added guests to booking {bookingId}")
        return booking
    except (NotFoundException, BadRequestException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, NotFoundException) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@router.post("/{bookingId}/payments", response_model=PaymentIntentResponse)
async def initiate_payment(
    bookingId: int,
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate payment for a booking
    
    Creates a Stripe payment intent and returns client secret for frontend
    
    **Note**: This is a placeholder. Full Stripe integration implemented in stripe_integration
    """
    booking = await BookingService.get_booking_by_id(db, bookingId, current_user.id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if not booking.guests or len(booking.guests) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add guests before making payment"
        )
    
    # TODO: Implement Stripe payment intent creation in stripe_integration module
    # For now, return mock data
    logger.warning(f"Mock payment intent created for booking {bookingId}")
    return PaymentIntentResponse(
        client_secret="pi_mock_secret_" + str(bookingId),
        payment_intent_id="pi_mock_" + str(bookingId)
    )


@router.post("/{bookingId}/cancel", response_model=BookingResponse)
async def cancel_booking(
    bookingId: int,
    cancellation_data: BookingCancellation,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a booking
    
    Cancellation policy:
    - More than 7 days before check-in: 100% refund
    - 2-7 days before check-in: 50% refund
    - Less than 2 days: No refund
    
    Returns the cancelled booking with refund information
    """
    try:
        booking = await BookingService.cancel_booking(
            db, bookingId, current_user.id, cancellation_data.reason
        )
        logger.info(f"Booking {bookingId} cancelled by user {current_user.id}")
        return booking
    except (NotFoundException, BadRequestException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, NotFoundException) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))
