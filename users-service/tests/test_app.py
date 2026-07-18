def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_signup_creates_user(client):
    response = client.post("/signup", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    # Password hash should never be exposed in the API response
    assert "password" not in data
    assert "password_hash" not in data


def test_signup_missing_fields_fails(client):
    response = client.post("/signup", json={"name": "No Email"})
    assert response.status_code == 400


def test_signup_duplicate_email_fails(client):
    client.post("/signup", json={
        "name": "First", "email": "dup@example.com", "password": "pass123"
    })
    response = client.post("/signup", json={
        "name": "Second", "email": "dup@example.com", "password": "pass456"
    })
    assert response.status_code == 409


def test_login_with_correct_credentials_returns_token(client):
    client.post("/signup", json={
        "name": "Login Test", "email": "login@example.com", "password": "mypassword"
    })
    response = client.post("/login", json={
        "email": "login@example.com", "password": "mypassword"
    })
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_with_wrong_password_fails(client):
    client.post("/signup", json={
        "name": "Login Test", "email": "wrongpass@example.com", "password": "correct"
    })
    response = client.post("/login", json={
        "email": "wrongpass@example.com", "password": "incorrect"
    })
    assert response.status_code == 401
