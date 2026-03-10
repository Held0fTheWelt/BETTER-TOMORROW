from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


def get_user_by_username(username):
    """Return User by username (case-insensitive) or None."""
    if not username or not isinstance(username, str):
        return None
    return User.query.filter(db.func.lower(User.username) == username.strip().lower()).first()


def verify_user(username, password):
    """Return User if username/password match, else None."""
    user = get_user_by_username(username)
    if user and password is not None and check_password_hash(user.password_hash, password):
        return user
    return None


def create_user(username, password):
    """
    Create a new user. Returns (user, None) or (None, error_message).
    """
    username = (username or "").strip()
    if not username:
        return None, "Username is required"
    if not password:
        return None, "Password is required"
    if len(username) < 2:
        return None, "Username must be at least 2 characters"
    if len(password) < 6:
        return None, "Password must be at least 6 characters"
    if get_user_by_username(username):
        return None, "Username already taken"
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user, None
