import logging
import re

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User

logger = logging.getLogger(__name__)

USERNAME_MAX_LENGTH = 80
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def validate_password(password: str) -> str | None:
    """Validate password. Returns error message or None if valid."""
    if not password:
        return "Password is required"
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    if len(password) > PASSWORD_MAX_LENGTH:
        return f"Password must be at most {PASSWORD_MAX_LENGTH} characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    return None


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
    if username:
        logger.warning("Failed login attempt for username=%r", username)
    return None


def create_user(username, password):
    """
    Create a new user. Returns (user, None) or (None, error_message).
    """
    username = (username or "").strip()
    if not username:
        return None, "Username is required"
    pw_error = validate_password(password)
    if pw_error:
        return None, pw_error
    if len(username) < 2:
        return None, "Username must be at least 2 characters"
    if len(username) > USERNAME_MAX_LENGTH:
        return None, f"Username must be at most {USERNAME_MAX_LENGTH} characters"
    if not USERNAME_PATTERN.match(username):
        return None, "Username contains invalid characters"
    if get_user_by_username(username):
        return None, "Username already taken"
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    logger.info("User created: id=%s username=%r", user.id, user.username)
    return user, None
