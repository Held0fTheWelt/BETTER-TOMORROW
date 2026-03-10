"""Public read-only news API. Only published news is exposed.

List:  GET /api/v1/news?q=&sort=published_at&direction=desc&page=1&limit=20&category=
  Response: { "items": [ { "id", "title", "slug", "summary", "content", "author_id", "author_name",
    "is_published", "published_at", "created_at", "updated_at", "cover_image", "category" } ], "total", "page", "per_page" }

Detail: GET /api/v1/news/<id>
  Response: single object same shape as list item, or { "error": "Not found" } 404.
"""
from datetime import datetime, timezone

from flask import jsonify, request

from app.api.v1 import api_v1_bp
from app.extensions import limiter
from app.services.news_service import (
    SORT_FIELDS,
    SORT_ORDERS,
    get_news_by_id,
    list_news,
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


@api_v1_bp.route("/news", methods=["GET"])
@limiter.limit("60 per minute")
def news_list():
    """
    List published news. Query params: q (search), sort, direction, page, limit, category.
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

    items, total = list_news(
        published_only=True,
        search=q,
        sort=sort,
        order=direction,
        page=page,
        per_page=limit,
        category=category,
    )
    return jsonify({
        "items": [n.to_dict() for n in items],
        "total": total,
        "page": page,
        "per_page": limit,
    }), 200


@api_v1_bp.route("/news/<int:news_id>", methods=["GET"])
@limiter.limit("60 per minute")
def news_detail(news_id):
    """
    Get a single published news article by id. 404 if not found or not published.
    Response: single news object (id, title, slug, summary, content, author_id, author_name, ...).
    """
    news = get_news_by_id(news_id)
    if not news or not news.is_published:
        return jsonify({"error": "Not found"}), 404
    now = datetime.now(timezone.utc)
    if news.published_at and news.published_at > now:
        return jsonify({"error": "Not found"}), 404
    return jsonify(news.to_dict()), 200
