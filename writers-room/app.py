"""
Writers Room – Flask mini-app for author workflow.

Currently hosts the "Almighty Oracle" page, but uses a shared admin-style layout
and supports login via the main backend API (JWT stored in session).
"""

import importlib.util
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

_here = Path(__file__).resolve().parent
_repo_root = _here.parent
_app_dir = _here / "app"

# Load .env from repo root (WorldOfShadows/.env). Fall back to current working dir.
_env_candidates = [
    Path.cwd() / ".env",
    _repo_root / ".env",
    _here / ".env",
]
for _p in _env_candidates:
    if _p.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(_p)
        except ImportError:
            pass
        break

_template_dir = (_app_dir / "templates") if (_app_dir / "templates").exists() else (_here / "templates")
_static_dir = (_app_dir / "static") if (_app_dir / "static").exists() else (_here / "static")

app = Flask(
    __name__,
    template_folder=str(_template_dir),
    static_folder=str(_static_dir),
)
app.secret_key = (
    os.environ.get("WRITERS_ROOM_SECRET_KEY")
    or os.environ.get("SECRET_KEY")
    or "writers-room-dev-secret-do-not-use-in-production"
)

BACKEND_BASE_URL = (
    os.environ.get("BACKEND_BASE_URL")
    or os.environ.get("BACKEND_API_URL")
    or "http://127.0.0.1:5000"
).rstrip("/")

_service_file = _here / "app" / "services" / "chatgpt_service.py"
_spec = importlib.util.spec_from_file_location("writers_room_chatgpt_service", str(_service_file))
_chatgpt_service = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
if _spec and _spec.loader:
    _spec.loader.exec_module(_chatgpt_service)  # type: ignore[call-arg]
else:  # pragma: no cover
    raise RuntimeError(f"Cannot load chatgpt service module from: {_service_file}")

get_oracle_answer = _chatgpt_service.get_oracle_answer


@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        print(f"[Oracle] User question: {question!r}")
        if question:
            answer = get_oracle_answer(question)
        else:
            answer = "You didn't ask anything. Try again!"
    return render_template("index.html", answer=answer)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login via backend API; stores JWT in session for later use."""
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("index"))
        return render_template("login.html", backend_base_url=BACKEND_BASE_URL)

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    if not username or not password:
        flash("Username and password are required.", "error")
        return render_template("login.html", backend_base_url=BACKEND_BASE_URL), 400

    try:
        payload = json.dumps({"username": username, "password": password}).encode("utf-8")
        req = urllib.request.Request(
            f"{BACKEND_BASE_URL}/api/v1/auth/login",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8"))
            msg = err.get("error") or "Login failed."
        except Exception:
            msg = "Login failed."
        flash(msg, "error")
        return render_template("login.html", backend_base_url=BACKEND_BASE_URL), 401
    except Exception:
        flash("Login failed (backend unreachable).", "error")
        return render_template("login.html", backend_base_url=BACKEND_BASE_URL), 502

    token = (data.get("access_token") or "").strip()
    if not token:
        flash("Login failed (no token).", "error")
        return render_template("login.html", backend_base_url=BACKEND_BASE_URL), 401

    session["access_token"] = token
    session["username"] = (data.get("user") or {}).get("username") or username
    flash(f"Welcome, {session['username']}.", "success")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
