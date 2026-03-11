"""Tests for User CRUD API. Aligned with Postman suite: List (admin), Get (self/other), Update, Delete."""
import pytest


def test_users_list_without_token_returns_401(client):
    """GET /api/v1/users without JWT returns 401."""
    r = client.get("/api/v1/users")
    assert r.status_code == 401
    assert r.get_json().get("error")


def test_users_list_as_admin_returns_200_and_structure(client, admin_headers):
    """GET /api/v1/users with admin JWT returns 200 and items, total, page, per_page."""
    r = client.get("/api/v1/users?page=1&limit=20", headers=admin_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert isinstance(data["items"], list)


def test_users_list_as_non_admin_returns_403(client, auth_headers):
    """GET /api/v1/users with non-admin JWT returns 403."""
    r = client.get("/api/v1/users", headers=auth_headers)
    assert r.status_code == 403
    assert r.get_json().get("error") == "Forbidden"


def test_users_get_self_returns_200(client, auth_headers, test_user):
    """GET /api/v1/users/<id> for own id returns 200 with id, username, role."""
    user, _ = test_user
    r = client.get(f"/api/v1/users/{user.id}", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert "role" in data


def test_users_get_as_admin_other_user_returns_200(client, app, admin_headers, test_user):
    """GET /api/v1/users/<id> as admin for another user returns 200."""
    user, _ = test_user
    r = client.get(f"/api/v1/users/{user.id}", headers=admin_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == user.id
    assert data["username"] == user.username


def test_users_get_as_non_admin_other_user_returns_403(client, app, auth_headers, admin_user):
    """GET /api/v1/users/<id> as non-admin for another user returns 403."""
    admin, _ = admin_user
    r = client.get(f"/api/v1/users/{admin.id}", headers=auth_headers)
    assert r.status_code == 403
    assert r.get_json().get("error") == "Forbidden"


def test_users_get_404(client, admin_headers):
    """GET /api/v1/users/999999 returns 404."""
    r = client.get("/api/v1/users/999999", headers=admin_headers)
    assert r.status_code == 404
    assert r.get_json().get("error")


def test_users_get_without_token_returns_401(client, test_user):
    """GET /api/v1/users/<id> without JWT returns 401."""
    user, _ = test_user
    r = client.get(f"/api/v1/users/{user.id}")
    assert r.status_code == 401


def test_users_update_self_returns_200(client, auth_headers, test_user):
    """PUT /api/v1/users/<id> for own id returns 200 and updated username."""
    user, _ = test_user
    r = client.put(
        f"/api/v1/users/{user.id}",
        headers=auth_headers,
        json={"username": "testuser_updated"},
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["username"] == "testuser_updated"
    assert data["id"] == user.id


def test_users_update_as_admin_other_user_returns_200(client, app, admin_headers, test_user):
    """PUT /api/v1/users/<id> as admin for another user returns 200."""
    user, _ = test_user
    r = client.put(
        f"/api/v1/users/{user.id}",
        headers=admin_headers,
        json={"username": "renamed_by_admin"},
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["username"] == "renamed_by_admin"


def test_users_update_as_non_admin_other_user_returns_403(client, app, auth_headers, admin_user):
    """PUT /api/v1/users/<id> as non-admin for another user returns 403."""
    admin, _ = admin_user
    r = client.put(
        f"/api/v1/users/{admin.id}",
        headers=auth_headers,
        json={"username": "hacker"},
        content_type="application/json",
    )
    assert r.status_code == 403
    assert r.get_json().get("error") == "Forbidden"


def test_users_update_404(client, admin_headers):
    """PUT /api/v1/users/999999 returns 404."""
    r = client.put(
        "/api/v1/users/999999",
        headers=admin_headers,
        json={"username": "x"},
        content_type="application/json",
    )
    assert r.status_code == 404


def test_users_delete_as_admin_returns_200(client, app, admin_headers, test_user):
    """DELETE /api/v1/users/<id> as admin for another user returns 200."""
    user, _ = test_user
    r = client.delete(f"/api/v1/users/{user.id}", headers=admin_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("message")
    with app.app_context():
        from app.models import User
        assert User.query.get(user.id) is None


def test_users_delete_as_non_admin_returns_403(client, app, auth_headers, admin_user):
    """DELETE /api/v1/users/<id> as non-admin returns 403."""
    admin, _ = admin_user
    r = client.delete(f"/api/v1/users/{admin.id}", headers=auth_headers)
    assert r.status_code == 403
    assert r.get_json().get("error") == "Forbidden"


def test_users_delete_404(client, admin_headers):
    """DELETE /api/v1/users/999999 returns 404."""
    r = client.delete("/api/v1/users/999999", headers=admin_headers)
    assert r.status_code == 404


def test_users_delete_without_token_returns_401(client, test_user):
    """DELETE /api/v1/users/<id> without JWT returns 401."""
    user, _ = test_user
    r = client.delete(f"/api/v1/users/{user.id}")
    assert r.status_code == 401
