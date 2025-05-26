import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_success():
    response = client.post(
        "/auth/register",
        json={
            "name": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "role": "user"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_register_duplicate():
    # Register the user first
    client.post(
        "/auth/register",
        json={
            "name": "duplicateuser",
            "email": "duplicate@example.com",
            "password": "testpassword",
            "role": "user"
        }
    )
    # Try to register again with the same email
    response = client.post(
        "/auth/register",
        json={
            "name": "duplicateuser2",
            "email": "duplicate@example.com",
            "password": "testpassword",
            "role": "user"
        }
    )
    assert response.status_code == 400
    assert "Usuário já existe" in response.text

def test_login_success():
    # Register user
    client.post(
        "/auth/register",
        json={
            "name": "loginuser",
            "email": "loginuser@example.com",
            "password": "testpassword",
            "role": "user"
        }
    )
    # Login
    response = client.post(
        "/auth/login",
        data={
            "name": "loginuser@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure():
    response = client.post(
        "/auth/login",
        data={
            "name": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_protected_endpoint_requires_auth():
    # Register and login
    client.post(
        "/auth/register",
        json={
            "name": "protecteduser",
            "email": "protecteduser@example.com",
            "password": "testpassword",
            "role": "user"
        }
    )
    login_response = client.post(
        "/auth/login",
        data={
            "name": "protecteduser@example.com",
            "password": "testpassword"
        }
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint (list users, requires admin, should fail for non-admin)
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should be 403 Forbidden for non-admin
    assert response.status_code in (401, 403)

    # Access user detail (should succeed for self)
    user_id = login_response.json()["user"]["id"]
    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "protecteduser@example.com"

def test_protected_endpoint_no_token():
    response = client.get("/users/")
    assert response.status_code == 401 or response.status_code == 403
