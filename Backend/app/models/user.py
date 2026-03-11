from datetime import datetime, timezone

from app.extensions import db


def _utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    """User for auth (web session and API JWT). Primary role via Role model. Supports ban state."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    email_verified_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    is_banned = db.Column(db.Boolean(), nullable=False, default=False)
    banned_at = db.Column(db.DateTime(timezone=True), nullable=True)
    ban_reason = db.Column(db.String(512), nullable=True)
    preferred_language = db.Column(db.String(10), nullable=True)
    last_seen_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=True, default=_utc_now)

    role_rel = db.relationship("Role", backref="users", lazy="joined")

    ROLE_USER = "user"
    ROLE_MODERATOR = "moderator"
    ROLE_ADMIN = "admin"

    @property
    def role(self) -> str:
        """Role name for API/templates. Use has_role / is_admin for checks."""
        return self.role_rel.name if self.role_rel else self.ROLE_USER

    def has_role(self, name: str) -> bool:
        """True if this user has the given role name."""
        return (self.role_rel and self.role_rel.name == name) or self.role == name

    def has_any_role(self, names) -> bool:
        """True if this user has any of the given role names."""
        r = self.role_rel.name if self.role_rel else self.role
        return r in names

    @property
    def is_admin(self) -> bool:
        """True if this user has admin role."""
        return self.has_role(self.ROLE_ADMIN)

    @property
    def is_moderator_or_admin(self) -> bool:
        """True if this user has moderator or admin role."""
        return self.has_any_role((self.ROLE_MODERATOR, self.ROLE_ADMIN))

    def to_dict(self, include_email: bool = False, include_ban: bool = False):
        out = {"id": self.id, "username": self.username, "role": self.role}
        if self.preferred_language is not None:
            out["preferred_language"] = self.preferred_language
        if include_email:
            out["email"] = self.email
        if include_ban:
            out["is_banned"] = self.is_banned
            out["banned_at"] = self.banned_at.isoformat() if self.banned_at else None
            out["ban_reason"] = self.ban_reason
        return out

    def can_write_news(self):
        """True if this user may create/update/delete/publish news (moderator or admin)."""
        return self.has_any_role((self.ROLE_MODERATOR, self.ROLE_ADMIN))

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"
