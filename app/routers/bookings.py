from fastapi import APIRouter

router = APIRouter()

@router.post("/init")
async def init_booking():
    return {"message": "Init Booking"}

@router.get("/{bookingId}/status")
async def booking_status(bookingId: int):
    return {"message": f"Booking {bookingId} Status"}

@router.post("/{bookingId}/addGuests")
async def add_guests_to_booking(bookingId: int):
    return {"message": f"Add Guests to Booking {bookingId}"}

@router.post("/{bookingId}/payments")
async def initiate_payment(bookingId: int):
    return {"message": f"Initiate Payment for Booking {bookingId}"}

@router.post("/{bookingId}/cancel")
async def cancel_booking(bookingId: int):
    return {"message": f"Cancel Booking {bookingId}"}
