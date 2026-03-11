"""Public site API: slogan resolution for placement (no auth)."""
from flask import current_app, jsonify, request

from app.api.v1 import api_v1_bp
from app.extensions import limiter
from app.services.slogan_service import resolve_slogan_for_placement


@api_v1_bp.route("/site/slogan", methods=["GET"])
@limiter.limit("120 per minute")
def site_slogan():
    """
    Resolve one slogan for a placement and language. Public endpoint.
    Query: placement (required), lang (optional, default from config).
    Returns { "text", "placement_key", "language_code" } or { "text": null } when no slogan.
    """
    placement = (request.args.get("placement") or "").strip()
    if not placement:
        return jsonify({"error": "placement is required"}), 400
    lang = (request.args.get("lang") or "").strip() or current_app.config.get("DEFAULT_LANGUAGE", "de")
    slogan = resolve_slogan_for_placement(placement, lang)
    if not slogan:
        return jsonify({"text": None, "placement_key": placement, "language_code": lang}), 200
    return jsonify({
        "text": slogan.text,
        "placement_key": slogan.placement_key,
        "language_code": slogan.language_code,
    }), 200
