"""Tests for web (server-rendered) routes."""
import pytest


def test_home_returns_200(client):
    """GET / returns 200 and renders home."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"World of Shadows" in response.data or b"Welcome" in response.data


def test_web_health_returns_ok(client):
    """GET /health returns JSON status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_login_get_returns_200(client):
    """GET /login shows login form."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"login" in response.data.lower() or b"username" in response.data.lower()


def test_login_post_invalid_credentials(client):
    """POST /login with wrong credentials shows error and does not redirect."""
    response = client.post(
        "/login",
        data={"username": "nobody", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"Invalid" in response.data or b"error" in response.data.lower()


def test_login_post_success_redirects_to_home(client, test_user):
    """POST /login with valid credentials redirects to home and sets session."""
    user, password = test_user
    response = client.post(
        "/login",
        data={"username": user.username, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"World of Shadows" in response.data


def test_logout_redirects_and_clears_session(client, test_user):
    """GET /logout redirects to home and clears session."""
    user, password = test_user
    client.post("/login", data={"username": user.username, "password": password})
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    # After logout, home should not show "logged in" state
    assert b"Log in" in response.data or b"login" in response.data.lower()


def test_404_returns_custom_page(client):
    """Unknown route returns 404 and custom template."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert b"not found" in response.data.lower() or b"404" in response.data
