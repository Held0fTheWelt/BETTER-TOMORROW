from __future__ import annotations

from typing import Any

from flask import jsonify, request, session
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.api.v1 import api_v1_bp
from app.extensions import db, limiter
from app.models import User
from app.services.game_service import (
    GameServiceConfigError,
    GameServiceError,
    create_run as create_play_run,
    get_play_service_websocket_url,
    issue_play_ticket,
    list_runs as list_play_runs,
    list_templates as list_play_templates,
    resolve_join_context,
)


def _current_user() -> User | None:
    uid = session.get("user_id")
    if uid is not None:
        return db.session.get(User, int(uid))
    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return None
    uid = get_jwt_identity()
    if uid is None:
        return None
    return db.session.get(User, int(uid))


def _require_game_user() -> User:
    user = _current_user()
    if user is None:
        raise PermissionError("Authentication required.")
    if getattr(user, "is_banned", False):
        raise PermissionError("Account is restricted.")
    return user


def _display_name_for(user: User, payload: dict[str, Any]) -> str:
    return (payload.get("character_name") or payload.get("display_name") or user.username or "Player").strip()


@api_v1_bp.route("/game/templates", methods=["GET"])
@limiter.limit("60 per minute")
def game_templates():
    try:
        _require_game_user()
        return jsonify({"templates": list_play_templates()})
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401 if "Authentication" in str(exc) else 403
    except GameServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@api_v1_bp.route("/game/runs", methods=["GET"])
@limiter.limit("60 per minute")
def game_runs():
    try:
        _require_game_user()
        return jsonify({"runs": list_play_runs()})
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401 if "Authentication" in str(exc) else 403
    except GameServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@api_v1_bp.route("/game/runs", methods=["POST"])
@limiter.limit("20 per minute")
def game_create_run():
    try:
        user = _require_game_user()
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401 if "Authentication" in str(exc) else 403

    data = request.get_json(silent=True) or {}
    template_id = (data.get("template_id") or "").strip()
    if not template_id:
        return jsonify({"error": "template_id is required."}), 400
    try:
        result = create_play_run(
            template_id=template_id,
            account_id=str(user.id),
            character_id=(data.get("character_id") or None),
            display_name=_display_name_for(user, data),
        )
        return jsonify(result), 200
    except GameServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@api_v1_bp.route("/game/tickets", methods=["POST"])
@limiter.limit("30 per minute")
def game_create_ticket():
    try:
        user = _require_game_user()
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401 if "Authentication" in str(exc) else 403

    data = request.get_json(silent=True) or {}
    run_id = (data.get("run_id") or "").strip()
    if not run_id:
        return jsonify({"error": "run_id is required."}), 400

    character_id = (data.get("character_id") or None)
    display_name = _display_name_for(user, data)
    preferred_role_id = (data.get("preferred_role_id") or None)

    try:
        join = resolve_join_context(
            run_id=run_id,
            account_id=str(user.id),
            character_id=character_id,
            display_name=display_name,
            preferred_role_id=preferred_role_id,
        )
        ticket = issue_play_ticket(
            {
                "run_id": join.run_id,
                "participant_id": join.participant_id,
                "account_id": str(user.id),
                "character_id": character_id,
                "display_name": join.display_name,
                "role_id": join.role_id,
            }
        )
        return jsonify(
            {
                "ticket": ticket,
                "run_id": join.run_id,
                "participant_id": join.participant_id,
                "role_id": join.role_id,
                "display_name": join.display_name,
                "ws_base_url": get_play_service_websocket_url(),
            }
        ), 200
    except GameServiceConfigError as exc:
        return jsonify({"error": str(exc)}), exc.status_code
    except GameServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code
