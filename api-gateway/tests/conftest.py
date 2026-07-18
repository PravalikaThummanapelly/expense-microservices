import os
import pytest

os.environ["USERS_SERVICE_URL"] = "http://users-service:5001"
os.environ["EXPENSES_SERVICE_URL"] = "http://expenses-service:5002"

from app import app as flask_app  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
