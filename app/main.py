from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from app.routers import auth, users, hotels, bookings, admin, webhook, health
from app.db.base import Base
from app.db.session import engine
from app.models import user, hotel  # Import models to register them
from app.core.logging_config import setup_logging
from app.core.middleware import setup_middleware
from app.core.exceptions import (
    AirbnbException,
    airbnb_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Airbnb API application")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down Airbnb API application")

app = FastAPI(
    title="Airbnb Backend API",
    version="2.0.0",
    description="A comprehensive hotel booking API with authentication, payments, and admin features",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Register exception handlers
app.add_exception_handler(AirbnbException, airbnb_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])

@app.get("/")
async def root():
    """Welcome endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Airbnb API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }
