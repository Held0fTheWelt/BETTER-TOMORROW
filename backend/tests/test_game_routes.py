from app.services.game_service import PlayJoinContext


def _login_session(client, username: str, password: str):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_game_menu_logged_in_renders_launcher(client, test_user):
    user, password = test_user
    _login_session(client, user.username, password)
    response = client.get("/game-menu")
    assert response.status_code == 200
    assert b"Game Menu" in response.data
    assert b"game_menu.js" in response.data


def test_game_templates_requires_auth(client):
    response = client.get("/api/v1/game/templates")
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_game_templates_proxy_uses_logged_in_session(client, test_user, monkeypatch):
    user, password = test_user
    _login_session(client, user.username, password)

    monkeypatch.setattr(
        "app.api.v1.game_routes.list_play_templates",
        lambda: [{"id": "god_of_carnage_solo", "title": "God of Carnage", "kind": "solo_story"}],
    )

    response = client.get("/api/v1/game/templates")
    assert response.status_code == 200
    data = response.get_json()
    assert data["templates"][0]["id"] == "god_of_carnage_solo"


def test_game_ticket_uses_backend_identity_and_returns_ws_url(client, auth_headers, test_user, monkeypatch):
    user, _ = test_user

    monkeypatch.setattr(
        "app.api.v1.game_routes.resolve_join_context",
        lambda **kwargs: PlayJoinContext(
            run_id=kwargs["run_id"],
            participant_id="participant-1",
            role_id="mediator",
            display_name=kwargs["display_name"],
            account_id=kwargs["account_id"],
            character_id=kwargs.get("character_id"),
        ),
    )
    monkeypatch.setattr("app.api.v1.game_routes.issue_play_ticket", lambda payload: f"signed-for-{payload['participant_id']}")
    monkeypatch.setattr("app.api.v1.game_routes.get_play_service_websocket_url", lambda: "wss://play.example.com")

    response = client.post(
        "/api/v1/game/tickets",
        json={"run_id": "run-1", "character_name": "Bruno"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["ticket"] == "signed-for-participant-1"
    assert data["ws_base_url"] == "wss://play.example.com"
    assert data["display_name"] == "Bruno"
