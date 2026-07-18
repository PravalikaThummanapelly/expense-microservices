import os
import pytest

# IMPORTANT: this must happen BEFORE we import app, because config.py reads
# environment variables at import time. Pointing at an in-memory SQLite
# database means our tests never need a real MySQL server running.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"

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
