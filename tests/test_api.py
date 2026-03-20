from fastapi.testclient import TestClient
from app.main import app
import pytest
import asyncio
import os
from app.db.session import async_session_factory
from app.models.user import User
from sqlalchemy import select

@pytest.fixture(scope="module")
def client():
    # Force clean DB for this module
    if os.path.exists("./test.db"):
        os.remove("./test.db")
        
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    if os.path.exists("./test.db"):
        os.remove("./test.db")

# Global state to share across tests
# In a real scenario, we might use classes or fixtures to pass data, 
# but globals work for this sequential test script.
state = {
    "user_email": "admin@example.com",
    "user_password": "password123",
    "access_token": None,
    "hotel_id": None,
    "room_id": None
}

def test_auth_signup(client):
    response = client.post("/auth/signup", json={
        "email": state["user_email"],
        "password": state["user_password"],
        "full_name": "Admin User"
    })
    assert response.status_code == 200
    assert response.json()["email"] == state["user_email"]

def test_auth_login(client):
    response = client.post("/auth/login", data={
        "username": state["user_email"],
        "password": state["user_password"]
    })
    assert response.status_code == 200
    state["access_token"] = response.json()["access_token"]

def test_make_superuser(client):
    """Helper to promote the user to superuser directly in DB"""
    async def _update():
        async with async_session_factory() as session:
            result = await session.execute(select(User).filter(User.email == state["user_email"]))
            user = result.scalars().first()
            if user:
                user.is_superuser = True
                session.add(user)
                await session.commit()
    
    # Run the async update function
    asyncio.run(_update())

def test_create_hotel_admin(client):
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    payload = {
        "name": "Grand Hotel",
        "location": "Paris",
        "description": "A lovely place",
        "image_url": "http://example.com/hotel.jpg",
        "is_active": False  # Created inactive
    }
    response = client.post("/admin/hotels", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Grand Hotel"
    state["hotel_id"] = data["id"]

def test_search_hotel_before_active(client):
    """Should not find the hotel yet because it is not active"""
    response = client.get("/hotels/search?location=Paris")
    assert response.status_code == 200
    data = response.json()
    found = any(h["id"] == state["hotel_id"] for h in data)
    assert not found

def test_activate_hotel(client):
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    response = client.patch(f"/admin/hotels/{state['hotel_id']}/activate", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Hotel activated"

def test_search_hotel_after_active(client):
    """Should find the hotel now"""
    response = client.get("/hotels/search?location=Paris")
    assert response.status_code == 200
    data = response.json()
    found = any(h["id"] == state["hotel_id"] for h in data)
    assert found

def test_create_room(client):
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    payload = {
        "name": "Deluxe Suite",
        "description": "Sea view",
        "price_per_night": 200.0,
        "capacity": 2,
        "is_available": True
    }
    response = client.post(f"/admin/hotels/{state['hotel_id']}/rooms", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Deluxe Suite"
    state["room_id"] = data["id"]

def test_get_hotel_details(client):
    """Public endpoint should show hotel and rooms"""
    response = client.get(f"/hotels/{state['hotel_id']}/info")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state["hotel_id"]
    assert len(data["rooms"]) == 1
    assert data["rooms"][0]["id"] == state["room_id"]

def test_update_room(client):
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    payload = {"price_per_night": 250.0}
    response = client.put(f"/admin/hotels/{state['hotel_id']}/rooms/{state['room_id']}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["price_per_night"] == 250.0

def test_delete_room(client):
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    response = client.delete(f"/admin/hotels/{state['hotel_id']}/rooms/{state['room_id']}", headers=headers)
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/hotels/{state['hotel_id']}/info")
    data = response.json()
    assert len(data["rooms"]) == 0

def test_delete_hotel(client):
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    response = client.delete(f"/admin/hotels/{state['hotel_id']}", headers=headers)
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/hotels/{state['hotel_id']}/info")
    assert response.status_code == 404
