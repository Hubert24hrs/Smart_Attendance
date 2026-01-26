def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user(client):
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    # Login
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    # Login with wrong password
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
