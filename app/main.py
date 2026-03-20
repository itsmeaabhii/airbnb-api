from fastapi import FastAPI
from app.routers import auth, users, hotels, bookings, admin, webhook
from app.db.base import Base
from app.db.session import engine
from app.models import user, hotel  # Import models to register them

app = FastAPI(title="Airbnb Backend API", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])

@app.get("/")
async def root():
    return {"message": "Welcome to Airbnb API"}
