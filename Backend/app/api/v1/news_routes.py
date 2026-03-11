"""Public read-only news API. Only published news is exposed.

List:  GET /api/v1/news?q=&sort=published_at&direction=desc&page=1&limit=20&category=
  Response: { "items": [ { "id", "title", "slug", "summary", "content", "author_id", "author_name",
    "is_published", "published_at", "created_at", "updated_at", "cover_image", "category" } ], "total", "page", "per_page" }

Detail: GET /api/v1/news/<id>
  Response: single object same shape as list item, or { "error": "Not found" } 404.

Write (all require Authorization: Bearer <JWT> and moderator/admin role; 401 if missing/invalid token, 403 if forbidden):
  POST   /api/v1/news             -> create (body: title, slug, content; optional summary, is_published, cover_image, category)
  PUT    /api/v1/news/<id>        -> update (body: optional title, slug, summary, content, cover_image, category)
  DELETE /api/v1/news/<id>        -> delete
  POST   /api/v1/news/<id>/publish   -> set published
  POST   /api/v1/news/<id>/unpublish -> set unpublished
"""
from datetime import datetime, timezone

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.v1 import api_v1_bp
from app.auth import current_user_can_write_news
from app.auth.permissions import get_current_user, require_jwt_moderator_or_admin
from app.extensions import limiter
from app.services import log_activity
from app.services.news_service import (
    SORT_FIELDS,
    SORT_ORDERS,
    create_news,
    delete_news,
    get_news_by_id,
    get_news_article_by_id,
    list_news,
    publish_news,
    unpublish_news,
    update_news,
)


def _parse_int(value, default, min_val=None, max_val=None):
    """Parse query param as int; return default if missing/invalid."""
    if value is None:
        return default
    try:
        n = int(value)
        if min_val is not None and n < min_val:
            return default
        if max_val is not None and n > max_val:
            return max_val
        return n
    except (TypeError, ValueError):
        return default


def _request_wants_include_drafts():
    """True if request has valid JWT with moderator/admin and query published_only=0 or include_drafts=1."""
    try:
        from flask_jwt_extended import get_jwt_identity
        raw = get_jwt_identity()
        if raw is None:
            return False
    except Exception:
        return False
    if not current_user_can_write_news():
        return False
    p = request.args.get("published_only", "").strip().lower()
    if p in ("0", "false", "no"):
        return True
    d = request.args.get("include_drafts", "").strip().lower()
    if d in ("1", "true", "yes"):
        return True
    return False


@api_v1_bp.route("/news", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def news_list():
    """
    List news. By default only published. With JWT (moderator/admin) and published_only=0 or include_drafts=1, includes drafts.
    Query params: q (search), sort, direction, page, limit, category, lang, published_only (0 to include drafts).
    Response: { "items": [...], "total": N, "page": P, "per_page": L }.
    """
    q = request.args.get("q", "").strip() or None
    sort = request.args.get("sort", "published_at").strip() or "published_at"
    if sort not in SORT_FIELDS:
        sort = "published_at"
    direction = request.args.get("direction", "desc").strip().lower() or "desc"
    if direction not in SORT_ORDERS:
        direction = "desc"
    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=100)
    category = request.args.get("category", "").strip() or None
    lang = request.args.get("lang", "").strip() or None
    published_only = not _request_wants_include_drafts()

    items, total = list_news(
        published_only=published_only,
        search=q,
        sort=sort,
        order=direction,
        page=page,
        per_page=limit,
        category=category,
        lang=lang,
    )
    return jsonify({
        "items": items,
        "total": total,
        "page": page,
        "per_page": limit,
    }), 200


@api_v1_bp.route("/news/<id_or_slug>", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def news_detail(id_or_slug):
    """
    Get a single news article by id (integer) or slug (string). Public: only published; 404 for draft.
    With JWT (moderator/admin): returns article even if draft. Query: lang for language.
    Response: single news object (id, title, slug, summary, content, author_id, author_name, language_code, ...).
    """
    lang = request.args.get("lang", "").strip() or None
    news = None
    if id_or_slug.isdigit():
        news = get_news_by_id(int(id_or_slug), lang=lang)
    else:
        news = get_news_by_slug(id_or_slug, lang=lang)
    if not news:
        return jsonify({"error": "Not found"}), 404
    if not news.get("is_published"):
        try:
            if get_jwt_identity() is not None and current_user_can_write_news():
                return jsonify(news), 200
        except Exception:
            pass
        return jsonify({"error": "Not found"}), 404
    now = datetime.now(timezone.utc)
    pub_at = news.get("published_at")
    if pub_at:
        try:
            dt = datetime.fromisoformat(pub_at.replace("Z", "+00:00")) if isinstance(pub_at, str) else pub_at
            if hasattr(dt, "tzinfo") and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt > now:
                return jsonify({"error": "Not found"}), 404
        except (ValueError, TypeError):
            pass
    return jsonify(news), 200


# --- Protected write endpoints (JWT required) ---


@api_v1_bp.route("/news", methods=["POST"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def news_create():
    """
    Create a news article. Requires JWT and moderator/admin role. Body: title, slug, content; optional summary, is_published, cover_image, category.
    author_id is set from JWT identity.
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    title = (data.get("title") or "").strip()
    slug = (data.get("slug") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not slug or not content:
        return jsonify({"error": "title, slug, and content are required"}), 400
    try:
        author_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid token"}), 401
    summary = data.get("summary")
    if summary is not None:
        summary = (summary or "").strip() or None
    is_published = bool(data.get("is_published", False))
    cover_image = data.get("cover_image")
    if cover_image is not None:
        cover_image = (cover_image or "").strip() or None
    category = data.get("category")
    if category is not None:
        category = (category or "").strip() or None

    article, err = create_news(
        title=title,
        slug=slug,
        content=content,
        summary=summary,
        author_id=author_id,
        is_published=is_published,
        cover_image=cover_image,
        category=category,
    )
    if err:
        status = 409 if err == "Slug already in use" else 400
        return jsonify({"error": err}), status
    log_activity(
        actor=get_current_user(),
        category="news",
        action="news_created",
        status="success",
        message=f"News created: {article.id}",
        route=request.path,
        method=request.method,
        target_type="news",
        target_id=str(article.id),
    )
    out = get_news_by_id(article.id, lang=article.default_language)
    return jsonify(out), 201


@api_v1_bp.route("/news/<int:article_id>", methods=["PUT"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def news_update(article_id):
    """
    Update a news article. Requires JWT and moderator/admin role. Body: optional title, slug, summary, content, cover_image, category.
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    kwargs = {}
    if "title" in data:
        kwargs["title"] = (data.get("title") or "").strip() or None
    if "slug" in data:
        kwargs["slug"] = (data.get("slug") or "").strip() or None
    if "summary" in data:
        kwargs["summary"] = (data.get("summary") or "").strip() or None
    if "content" in data:
        kwargs["content"] = (data.get("content") or "").strip() or None
    if "cover_image" in data:
        kwargs["cover_image"] = (data.get("cover_image") or "").strip() or None
    if "category" in data:
        kwargs["category"] = (data.get("category") or "").strip() or None

    article, err = update_news(article_id, **kwargs)
    if err:
        status = 409 if err == "Slug already in use" else (404 if err == "News not found" else 400)
        return jsonify({"error": err}), status
    log_activity(
        actor=get_current_user(),
        category="news",
        action="news_updated",
        status="success",
        message=f"News updated: {article.id}",
        route=request.path,
        method=request.method,
        target_type="news",
        target_id=str(article.id),
    )
    out = get_news_by_id(article.id, lang=article.default_language)
    return jsonify(out), 200


@api_v1_bp.route("/news/<int:article_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def news_delete(article_id):
    """Delete a news article. Requires JWT and moderator/admin role."""
    ok, err = delete_news(article_id)
    if err:
        return jsonify({"error": err}), 404
    log_activity(
        actor=get_current_user(),
        category="news",
        action="news_deleted",
        status="success",
        message=f"News deleted: id={article_id}",
        route=request.path,
        method=request.method,
        target_type="news",
        target_id=str(article_id),
    )
    return jsonify({"message": "Deleted"}), 200


@api_v1_bp.route("/news/<int:article_id>/publish", methods=["POST"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def news_publish(article_id):
    """Set article as published. Requires JWT and moderator/admin role."""
    article, err = publish_news(article_id)
    if err:
        return jsonify({"error": err}), 404
    log_activity(
        actor=get_current_user(),
        category="news",
        action="news_published",
        status="success",
        message=f"News published: {article.id}",
        route=request.path,
        method=request.method,
        target_type="news",
        target_id=str(article.id),
    )
    out = get_news_by_id(article.id, lang=article.default_language)
    return jsonify(out), 200


@api_v1_bp.route("/news/<int:article_id>/unpublish", methods=["POST"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def news_unpublish(article_id):
    """Set article as unpublished. Requires JWT and moderator/admin role."""
    article, err = unpublish_news(article_id)
    if err:
        return jsonify({"error": err}), 404
    log_activity(
        actor=get_current_user(),
        category="news",
        action="news_unpublished",
        status="success",
        message=f"News unpublished: {article.id}",
        route=request.path,
        method=request.method,
        target_type="news",
        target_id=str(article.id),
    )
    out = get_news_by_id(article.id, lang=article.default_language)
    return jsonify(out), 200
