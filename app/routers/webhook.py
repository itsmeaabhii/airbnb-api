from fastapi import APIRouter

router = APIRouter()

@router.post("/payment")
async def payment_webhook():
    return {"message": "Payment Webhook"}
