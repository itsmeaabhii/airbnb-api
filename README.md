# Airbnb Backend API — Python & FastAPI

This is the Python + FastAPI version of the Airbnb Backend API, providing the same set of RESTful endpoints for hotel management, booking flow, user authentication, and more.

![Schema](https://github.com/user-attachments/assets/bc209296-e0f2-48f9-a7ae-65d084e4cb6c)

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** SQLAlchemy (async)
- **Database:** PostgreSQL
- **Auth:** JWT (OAuth2 Password Flow)
- **Payments:** Stripe Webhook Integration
- **Docs:** Auto-generated via Swagger UI (`/docs`) and ReDoc (`/redoc`)

---

## Features

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

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL
- pip / virtualenv

### Installation

```bash
# Clone the repository
git clone https://github.com/itsmeaabhii/airbnb-api.git
cd airbnb-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/airbnb
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### Run the Application

```bash
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## Project Structure

```
airbnb-api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # App configuration
│   │   └── security.py      # JWT utilities
│   ├── db/
│   │   ├── base.py          # SQLAlchemy base
│   │   └── session.py       # DB session
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # FastAPI routers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── hotels.py
│   │   ├── bookings.py
│   │   ├── admin.py
│   │   └── webhook.py
│   └── services/            # Business logic
├── requirements.txt
├── .env.example
└── README.md
```

---

## License

This project is licensed under the MIT License.
