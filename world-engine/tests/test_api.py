from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.http import router as http_router
from app.api.ws import router as ws_router
from app.auth.tickets import TicketManager
from app.runtime.manager import RuntimeManager


def build_test_app(tmp_path: Path) -> FastAPI:
    app = FastAPI()
    app.state.manager = RuntimeManager(store_root=tmp_path)
    app.state.ticket_manager = TicketManager("test-secret")
    app.include_router(http_router)
    app.include_router(ws_router)
    return app


def test_create_run_and_ticket_include_backend_identity(tmp_path: Path):
    app = build_test_app(tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/runs",
        json={"template_id": "god_of_carnage_solo", "account_id": "42", "display_name": "Hollywood"},
    )
    assert response.status_code == 200
    run_id = response.json()["run"]["id"]

    ticket_response = client.post(
        "/api/tickets",
        json={"run_id": run_id, "account_id": "42", "display_name": "Hollywood"},
    )
    assert ticket_response.status_code == 200
    payload = app.state.ticket_manager.verify(ticket_response.json()["ticket"])
    assert payload["account_id"] == "42"
    assert payload["display_name"] == "Hollywood"


def test_internal_join_context_reuses_same_account_seat(tmp_path: Path):
    app = build_test_app(tmp_path)
    client = TestClient(app)

    run_response = client.post(
        "/api/runs",
        json={"template_id": "apartment_confrontation_group", "account_id": "100", "display_name": "Host"},
    )
    run_id = run_response.json()["run"]["id"]

    first = client.post(
        "/api/internal/join-context",
        json={"run_id": run_id, "account_id": "100", "display_name": "Host"},
    )
    second = client.post(
        "/api/internal/join-context",
        json={"run_id": run_id, "account_id": "100", "display_name": "Host Updated"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["participant_id"] == second.json()["participant_id"]
    assert second.json()["display_name"] == "Host Updated"


def test_websocket_move_flow(tmp_path: Path):
    app = build_test_app(tmp_path)
    client = TestClient(app)

    run_response = client.post(
        "/api/runs",
        json={"template_id": "god_of_carnage_solo", "account_id": "7", "display_name": "Hollywood"},
    )
    run_id = run_response.json()["run"]["id"]
    ticket_response = client.post(
        "/api/tickets",
        json={"run_id": run_id, "account_id": "7", "display_name": "Hollywood"},
    )
    ticket = ticket_response.json()["ticket"]

    with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
        first_payload = websocket.receive_json()
        assert first_payload["type"] == "snapshot"
        assert first_payload["data"]["viewer_room_id"] == "hallway"

        websocket.send_json({"action": "move", "target_room_id": "living_room"})
        second_payload = websocket.receive_json()
        assert second_payload["type"] == "snapshot"
        assert second_payload["data"]["viewer_room_id"] == "living_room"
        assert any(entry["kind"] == "room_changed" for entry in second_payload["data"]["transcript_tail"])
