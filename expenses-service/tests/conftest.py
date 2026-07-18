import os
import jwt
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["USERS_SERVICE_URL"] = "http://users-service:5001"

from app import app as flask_app, db  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            db.create_all()
        yield client
        with flask_app.app_context():
            db.session.remove()
            db.drop_all()


@pytest.fixture
def auth_headers():
    """
    expenses-service doesn't issue tokens itself (users-service does), so for
    tests we craft one directly using the same secret — this is exactly what
    users-service would have produced at login.
    """
    token = jwt.encode({"user_id": 1}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}
