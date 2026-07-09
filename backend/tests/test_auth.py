def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_first_user_becomes_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@pharmacy.com",
            "username": "admin",
            "password": "securepass123",
            "full_name": "System Admin",
            "phone": "+91-9876543210",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@pharmacy.com"
    assert data["role"]["name"] == "admin"


def test_login_and_get_profile(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "manager@store.com",
            "username": "manager",
            "password": "securepass123",
            "full_name": "Store Manager",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "manager", "password": "securepass123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "manager"


def test_login_invalid_credentials(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@test.com",
            "username": "user1",
            "password": "securepass123",
            "full_name": "Test User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "user1", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_refresh_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@test.com",
            "username": "refreshuser",
            "password": "securepass123",
            "full_name": "Refresh User",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "refreshuser", "password": "securepass123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_duplicate_email_registration(client):
    payload = {
        "email": "dup@test.com",
        "username": "user_a",
        "password": "securepass123",
        "full_name": "User A",
    }
    client.post("/api/v1/auth/register", json=payload)

    payload["username"] = "user_b"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_unauthorized_access(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
