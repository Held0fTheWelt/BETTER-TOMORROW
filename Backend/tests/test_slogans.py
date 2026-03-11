"""Tests for slogan CRUD API and site slogan resolution."""
import pytest


def test_site_slogan_public_no_auth(client):
    """GET /api/v1/site/slogan?placement=landing.teaser.primary is public (no 401)."""
    r = client.get("/api/v1/site/slogan?placement=landing.teaser.primary&lang=de")
    assert r.status_code == 200
    data = r.get_json()
    assert "text" in data
    assert data["placement_key"] == "landing.teaser.primary"
    assert data["language_code"] == "de"


def test_site_slogan_requires_placement(client):
    """GET /api/v1/site/slogan without placement returns 400."""
    r = client.get("/api/v1/site/slogan?lang=de")
    assert r.status_code == 400


def test_slogans_list_requires_auth(client):
    """GET /api/v1/slogans without token returns 401."""
    r = client.get("/api/v1/slogans")
    assert r.status_code == 401


def test_slogans_list_moderator_returns_200(client, moderator_headers):
    """GET /api/v1/slogans as moderator returns 200 and items array."""
    r = client.get("/api/v1/slogans", headers=moderator_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_slogans_create_and_resolve(client, moderator_headers):
    """Create a slogan via API then resolve it via site/slogan."""
    payload = {
        "text": "Test slogan for placement.",
        "category": "landing_teaser",
        "placement_key": "landing.teaser.primary",
        "language_code": "de",
        "is_active": True,
    }
    r = client.post("/api/v1/slogans", headers=moderator_headers, json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data["text"] == payload["text"]
    assert data["placement_key"] == payload["placement_key"]
    slogan_id = data["id"]

    r2 = client.get("/api/v1/site/slogan?placement=landing.teaser.primary&lang=de")
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2.get("text") == payload["text"]

    r3 = client.delete("/api/v1/slogans/" + str(slogan_id), headers=moderator_headers)
    assert r3.status_code == 200


def test_slogans_create_invalid_category_rejected(client, moderator_headers):
    """POST /api/v1/slogans with invalid category returns 400."""
    r = client.post(
        "/api/v1/slogans",
        headers=moderator_headers,
        json={
            "text": "x",
            "category": "invalid_category",
            "placement_key": "landing.teaser.primary",
            "language_code": "de",
        },
    )
    assert r.status_code == 400


def test_slogan_deactivate_then_resolve_returns_null(client, moderator_headers):
    """After deactivating a slogan, site/slogan returns text null or different."""
    payload = {
        "text": "Only active slogan here",
        "category": "landing_teaser",
        "placement_key": "landing.ad.primary",
        "language_code": "de",
        "is_active": True,
    }
    r = client.post("/api/v1/slogans", headers=moderator_headers, json=payload)
    assert r.status_code == 201
    sid = r.get_json()["id"]
    r2 = client.get("/api/v1/site/slogan?placement=landing.ad.primary&lang=de")
    assert r2.status_code == 200
    assert r2.get_json().get("text") == payload["text"]
    r3 = client.post("/api/v1/slogans/" + str(sid) + "/deactivate", headers=moderator_headers)
    assert r3.status_code == 200
    r4 = client.get("/api/v1/site/slogan?placement=landing.ad.primary&lang=de")
    assert r4.status_code == 200
    assert r4.get_json().get("text") is None
    client.delete("/api/v1/slogans/" + str(sid), headers=moderator_headers)
