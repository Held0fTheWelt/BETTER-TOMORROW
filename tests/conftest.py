"""Pytest fixtures for World of Shadows."""
import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Application with testing config and in-memory DB."""
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application


@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for flask commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user in the DB; returns (user, password)."""
    with app.app_context():
        user = User(
            username="testuser",
            password_hash=generate_password_hash("testpass"),
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user, "testpass"


@pytest.fixture
def auth_headers(test_user, client):
    """Return headers with valid JWT for test_user (for API requests)."""
    user, password = test_user
    response = client.post(
        "/api/v1/auth/login",
        json={"username": user.username, "password": password},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
