"""Tests for wiki API: GET and PUT /api/v1/wiki (moderator/admin only)."""
import pytest


def test_wiki_get_without_auth_returns_401(client):
    """GET /api/v1/wiki without Authorization returns 401."""
    response = client.get("/api/v1/wiki")
    assert response.status_code == 401


def test_wiki_get_with_user_role_returns_403(client, auth_headers):
    """GET /api/v1/wiki with JWT for plain user returns 403."""
    response = client.get("/api/v1/wiki", headers=auth_headers)
    assert response.status_code == 403


def test_wiki_get_with_moderator_returns_200(client, moderator_headers, tmp_path, monkeypatch):
    """GET /api/v1/wiki with moderator JWT returns 200 and content/html."""
    wiki_file = tmp_path / "wiki.md"
    wiki_file.write_text("# Hello\n\nWiki content.", encoding="utf-8")

    from app.api.v1 import wiki_routes
    def fake_path():
        return wiki_file
    monkeypatch.setattr(wiki_routes, "_wiki_path", fake_path)

    response = client.get("/api/v1/wiki", headers=moderator_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "content" in data
    assert data["content"] == "# Hello\n\nWiki content."
    assert "html" in data
    assert "Hello" in (data["html"] or "")


def test_wiki_get_missing_file_returns_empty_content(client, moderator_headers, tmp_path, monkeypatch):
    """GET /api/v1/wiki when file does not exist returns 200 with empty content."""
    wiki_file = tmp_path / "wiki.md"
    assert not wiki_file.exists()

    from app.api.v1 import wiki_routes
    def fake_path():
        return wiki_file
    monkeypatch.setattr(wiki_routes, "_wiki_path", fake_path)

    response = client.get("/api/v1/wiki", headers=moderator_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("content") == ""
    assert data.get("html") is None


def test_wiki_put_without_auth_returns_401(client):
    """PUT /api/v1/wiki without Authorization returns 401."""
    response = client.put(
        "/api/v1/wiki",
        json={"content": "# Updated"},
        content_type="application/json",
    )
    assert response.status_code == 401


def test_wiki_put_with_moderator_writes_file(client, moderator_headers, tmp_path, monkeypatch):
    """PUT /api/v1/wiki with moderator JWT writes content and returns 200."""
    wiki_file = tmp_path / "wiki.md"
    wiki_file.parent.mkdir(parents=True, exist_ok=True)
    wiki_file.write_text("old", encoding="utf-8")

    from app.api.v1 import wiki_routes
    def fake_path():
        return wiki_file
    monkeypatch.setattr(wiki_routes, "_wiki_path", fake_path)

    response = client.put(
        "/api/v1/wiki",
        json={"content": "# New content\n\nUpdated."},
        content_type="application/json",
        headers=moderator_headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("message") == "Updated"
    assert data.get("content") == "# New content\n\nUpdated."
    assert wiki_file.read_text(encoding="utf-8") == "# New content\n\nUpdated."


def test_wiki_put_without_body_returns_400(client, moderator_headers, tmp_path, monkeypatch):
    """PUT /api/v1/wiki without JSON body returns 400."""
    wiki_file = tmp_path / "wiki.md"
    from app.api.v1 import wiki_routes
    monkeypatch.setattr(wiki_routes, "_wiki_path", lambda: wiki_file)

    response = client.put("/api/v1/wiki", headers=moderator_headers)
    assert response.status_code == 400
    assert response.get_json().get("error")


def test_wiki_put_without_content_key_returns_400(client, moderator_headers, tmp_path, monkeypatch):
    """PUT /api/v1/wiki with body missing 'content' returns 400."""
    wiki_file = tmp_path / "wiki.md"
    from app.api.v1 import wiki_routes
    monkeypatch.setattr(wiki_routes, "_wiki_path", lambda: wiki_file)

    response = client.put(
        "/api/v1/wiki",
        json={},
        content_type="application/json",
        headers=moderator_headers,
    )
    assert response.status_code == 400
    assert "content" in (response.get_json().get("error") or "").lower()


# ============= WIKI PUBLIC PAGE ENDPOINT TESTS =============


def test_wiki_public_page_get_returns_200(app, client):
    """GET /api/v1/wiki/<slug> returns 200 with title, slug, content_markdown, html."""
    from app.extensions import db
    from app.models.wiki_page import WikiPage, WikiPageTranslation

    with app.app_context():
        page = WikiPage(key="intro", is_published=True)
        db.session.add(page)
        db.session.flush()
        trans = WikiPageTranslation(
            page_id=page.id,
            language_code="de",
            title="Introduction",
            slug="introduction",
            content_markdown="# Hello World",
            translation_status="approved",
        )
        db.session.add(trans)
        db.session.commit()

    response = client.get("/api/v1/wiki/introduction")
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Introduction"
    assert data["slug"] == "introduction"
    assert "content_markdown" in data
    assert "html" in data


def test_wiki_public_page_not_found_returns_404(client):
    """GET /api/v1/wiki/nonexistent returns 404."""
    response = client.get("/api/v1/wiki/nonexistent-slug-xyz")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_wiki_public_page_has_discussion_thread_fields(app, client):
    """GET /api/v1/wiki/<slug> response includes discussion_thread_id and discussion_thread_slug."""
    from app.extensions import db
    from app.models.wiki_page import WikiPage, WikiPageTranslation

    with app.app_context():
        page = WikiPage(key="about", is_published=True)
        db.session.add(page)
        db.session.flush()
        trans = WikiPageTranslation(
            page_id=page.id,
            language_code="de",
            title="About",
            slug="about-page",
            content_markdown="About content.",
            translation_status="approved",
        )
        db.session.add(trans)
        db.session.commit()

    response = client.get("/api/v1/wiki/about-page")
    assert response.status_code == 200
    data = response.get_json()
    assert "discussion_thread_id" in data
    assert "discussion_thread_slug" in data


def test_wiki_public_page_discussion_thread_null_when_not_linked(app, client):
    """discussion_thread_id and discussion_thread_slug are None for unlinked wiki page."""
    from app.extensions import db
    from app.models.wiki_page import WikiPage, WikiPageTranslation

    with app.app_context():
        page = WikiPage(key="rules", is_published=True)
        db.session.add(page)
        db.session.flush()
        trans = WikiPageTranslation(
            page_id=page.id,
            language_code="de",
            title="Rules",
            slug="rules-page",
            content_markdown="Game rules.",
            translation_status="approved",
        )
        db.session.add(trans)
        db.session.commit()

    response = client.get("/api/v1/wiki/rules-page")
    assert response.status_code == 200
    data = response.get_json()
    assert data["discussion_thread_id"] is None
    assert data["discussion_thread_slug"] is None


def test_wiki_link_discussion_thread_requires_auth(app, client):
    """POST /api/v1/wiki/<id>/discussion-thread without auth returns 401."""
    from app.extensions import db
    from app.models.wiki_page import WikiPage, WikiPageTranslation

    with app.app_context():
        page = WikiPage(key="lore", is_published=True)
        db.session.add(page)
        db.session.flush()
        trans = WikiPageTranslation(
            page_id=page.id,
            language_code="en",
            title="Lore",
            slug="lore-page",
            content_markdown="Lore content.",
            translation_status="approved",
        )
        db.session.add(trans)
        db.session.commit()
        page_id = page.id

    resp = client.post(
        "/api/v1/wiki/{}/discussion-thread".format(page_id),
        json={"discussion_thread_id": 1},
    )
    assert resp.status_code == 401


def test_wiki_link_discussion_thread_moderator_can_link(app, client, moderator_headers):
    """POST /api/v1/wiki/<id>/discussion-thread with valid thread links it (moderator)."""
    from app.extensions import db
    from app.models.wiki_page import WikiPage, WikiPageTranslation
    from app.models.forum import ForumCategory, ForumThread

    with app.app_context():
        page = WikiPage(key="history", is_published=True)
        db.session.add(page)
        db.session.flush()
        trans = WikiPageTranslation(
            page_id=page.id,
            language_code="en",
            title="History",
            slug="history-page",
            content_markdown="History.",
            translation_status="approved",
        )
        db.session.add(trans)
        cat = ForumCategory(slug="wiki-disc-cat", title="Wiki Disc", is_active=True, is_private=False)
        db.session.add(cat)
        db.session.flush()
        thread = ForumThread(
            category_id=cat.id,
            slug="wiki-disc-thread",
            title="Wiki Discussion",
            status="open",
        )
        db.session.add(thread)
        db.session.commit()
        page_id = page.id
        thread_id = thread.id

    resp = client.post(
        "/api/v1/wiki/{}/discussion-thread".format(page_id),
        json={"discussion_thread_id": thread_id},
        headers=moderator_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("discussion_thread_id") == thread_id
