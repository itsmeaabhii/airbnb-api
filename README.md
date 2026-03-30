# Airbnb Backend API — Python & FastAPI

This is the Python + FastAPI version of the Airbnb Backend API, providing the same set of RESTful endpoints for hotel management, booking flow, user authentication, and more.

![Schema](https://github.com/user-attachments/assets/bc209296-e0f2-48f9-a7ae-65d084e4cb6c)

---

## ✨ What's New in v2.0

- ✅ **Modernized Codebase**: Updated to Pydantic v2 and SQLAlchemy 2.0
- ✅ **Structured Logging**: Comprehensive logging throughout the application
- ✅ **Error Handling**: Custom exception handlers and detailed error messages
- ✅ **Security Enhanced**: CORS, security headers, and middleware
- ✅ **Health Checks**: `/health` and `/health/db` endpoints for monitoring
- ✅ **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- ✅ **Database Migrations**: Alembic integration for schema management
- ✅ **Zero Deprecation Warnings**: All code follows modern best practices

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL
- **Auth:** JWT (OAuth2 Password Flow)
- **Payments:** Stripe Webhook Integration
- **Migrations:** Alembic
- **Docs:** Auto-generated via Swagger UI (`/docs`) and ReDoc (`/redoc`)

---

## Features

### Health & Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/db` | Database connectivity check |

### User Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login and receive JWT tokens |
| POST | `/auth/refresh` | Refresh access token |

### User Profile & Guests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/profile` | Get my profile |
| PATCH | `/users/profile` | Update my profile |
| GET | `/users/guests` | Get my saved guests |
| POST | `/users/guests` | Add a guest |
| PUT | `/users/guests/{guestId}` | Update a guest |
| DELETE | `/users/guests/{guestId}` | Remove a guest |
| GET | `/users/myBookings` | Get my bookings |

### Hotel Browse
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hotels/search` | Search for hotels |
| GET | `/hotels/{hotelId}/info` | Get hotel details |

### Booking Flow
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bookings/init` | Initialize a new booking |
| GET | `/bookings/{bookingId}/status` | Check booking status |
| POST | `/bookings/{bookingId}/addGuests` | Add guests to a booking |
| POST | `/bookings/{bookingId}/payments` | Initiate payment |
| POST | `/bookings/{bookingId}/cancel` | Cancel a booking |

### Admin — Hotel Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/hotels` | Get all admin hotels |
| POST | `/admin/hotels` | Create a hotel |
| GET | `/admin/hotels/{hotelId}` | Get hotel by ID |
| PUT | `/admin/hotels/{hotelId}` | Update hotel details |
| DELETE | `/admin/hotels/{hotelId}` | Delete a hotel |
| PATCH | `/admin/hotels/{hotelId}/activate` | Activate a hotel |

### Admin — Room Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/hotels/{hotelId}/rooms` | Get all rooms |
| POST | `/admin/hotels/{hotelId}/rooms` | Create a room |
| GET | `/admin/hotels/{hotelId}/rooms/{roomId}` | Get room details |
| PUT | `/admin/hotels/{hotelId}/rooms/{roomId}` | Update a room |
| DELETE | `/admin/hotels/{hotelId}/rooms/{roomId}` | Delete a room |

### Admin — Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/inventory/rooms/{roomId}` | Get room inventory |
| PATCH | `/admin/inventory/rooms/{roomId}` | Update room inventory |

### Admin — Reports & Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/hotels/{hotelId}/bookings` | Get all bookings for a hotel |
| GET | `/admin/hotels/{hotelId}/reports` | Generate hotel booking report |

### Webhook
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhook/payment` | Capture payment events (Stripe) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL (or use Docker)
- pip / virtualenv

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/itsmeaabhii/airbnb-api.git
cd airbnb-api

# Start all services with Docker Compose
docker-compose up -d

# API will be available at: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/itsmeaabhii/airbnb-api.git
cd airbnb-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see below)
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/airbnb
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`  
Health Check: `http://localhost:8000/health`

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📁 Project Structure

```
airbnb-api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # App configuration
│   │   ├── security.py      # JWT utilities
│   │   ├── logging_config.py # Logging setup
│   │   ├── middleware.py    # CORS & security middleware
│   │   └── exceptions.py    # Custom exceptions & handlers
│   ├── db/
│   │   ├── base.py          # SQLAlchemy base
│   │   └── session.py       # DB session
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   └── hotel.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── hotel.py
│   │   └── token.py
│   ├── routers/             # FastAPI routers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── hotels.py
│   │   ├── bookings.py
│   │   ├── admin.py
│   │   ├── webhook.py
│   │   └── health.py        # Health check endpoints
│   └── services/            # Business logic
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                   # Test suite
│   └── test_api.py
├── logs/                    # Application logs
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker Compose configuration
├── alembic.ini             # Alembic configuration
├── requirements.txt
├── .env.example
├── .gitignore
├── .dockerignore
└── README.md
```

---

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **CORS**: Configurable Cross-Origin Resource Sharing
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, HSTS
- **Request Logging**: All requests are logged for audit trails
- **Input Validation**: Pydantic schemas for data validation

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t airbnb-api .

# Run the container
docker run -d -p 8000:8000 --env-file .env airbnb-api

# Or use docker-compose
docker-compose up -d
```

### Docker Compose Services

- **db**: PostgreSQL 15 database
- **api**: FastAPI application

Both services include health checks and automatic restart policies.

---

## 📊 Monitoring & Health Checks

The API includes built-in health check endpoints:

- `GET /health` - Basic application health
- `GET /health/db` - Database connectivity check

Use these endpoints with monitoring tools like:
- Kubernetes liveness/readiness probes
- Docker health checks
- Uptime monitoring services

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

---

## 📝 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API documentation with the ability to test endpoints directly.

---

## 🛠️ Development

### Code Quality

```bash
# Format code with black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

### Database Management

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Add new field to User model"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for powerful ORM capabilities
- Pydantic for data validation
- Alembic for database migrations
