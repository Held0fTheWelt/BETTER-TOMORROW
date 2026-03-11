"""Lightweight Flask public frontend for World of Shadows.
Serves HTML and static assets only; consumes backend API for data. No database."""
import os
from flask import Flask, render_template

# Backend API base URL (no trailing slash). Used for login link and for frontend JS.
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:5000").rstrip("/")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)
app.config["BACKEND_API_URL"] = BACKEND_API_URL


@app.context_processor
def inject_config():
    """Expose backend URL and frontend config to all templates."""
    return {
        "backend_api_url": app.config["BACKEND_API_URL"],
        "frontend_config": {
            "backendApiUrl": app.config["BACKEND_API_URL"],
        },
    }


@app.route("/")
def index():
    """Public home page."""
    return render_template("index.html")


@app.route("/news")
def news_list():
    """Public news list page. Data loaded by JS from backend API."""
    return render_template("news.html")


@app.route("/news/<int:news_id>")
def news_detail(news_id):
    """Public news detail page. Data loaded by JS from backend API."""
    return render_template("news_detail.html", news_id=news_id)


# --- Management / editorial area (protected by frontend auth; backend enforces roles) ---

@app.route("/manage")
def manage_index():
    """Management area entry; redirects to login or dashboard (news)."""
    return render_template("manage/dashboard.html")


@app.route("/manage/login")
def manage_login():
    """Management login page (JWT via backend API)."""
    return render_template("manage/login.html")


@app.route("/manage/news")
def manage_news():
    """News management (list, create, edit, publish, unpublish, delete)."""
    return render_template("manage/news.html")


@app.route("/manage/users")
def manage_users():
    """User administration (admin only; table, edit, role, ban, unban)."""
    return render_template("manage/users.html")


@app.route("/manage/wiki")
def manage_wiki():
    """Wiki editor (markdown source, preview, save)."""
    return render_template("manage/wiki.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "0").strip().lower() in ("1", "true", "yes", "on")
    app.run(host="0.0.0.0", port=port, debug=debug)
