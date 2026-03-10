from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services import verify_user

web_bp = Blueprint("web", __name__)


@web_bp.route("/health")
def health():
    """Web health check (HTML or simple text)."""
    return {"status": "ok"}, 200


@web_bp.route("/")
def home():
    """Home page."""
    return render_template("home.html")


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """Session-based login."""
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password")
        if not username or password is None:
            flash("Username and password are required.", "error")
            return render_template("login.html")
        user = verify_user(username, password)
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome, {user.username}.", "success")
            return redirect(url_for("web.home"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@web_bp.route("/logout")
def logout():
    """Clear session and redirect to home."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("web.home"))
