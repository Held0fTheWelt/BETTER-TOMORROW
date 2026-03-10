"""Application entry point."""
import os
from app import create_app
from app.extensions import db

app = create_app()


@app.cli.command("init-db")
def init_db():
    """Create tables and optionally seed a test user."""
    db.create_all()
    from app.models import User
    if User.query.filter_by(username="admin").first() is None:
        from werkzeug.security import generate_password_hash
        u = User(username="admin", password_hash=generate_password_hash("admin"))
        db.session.add(u)
        db.session.commit()
        print("Created default user: admin / admin")
    print("Database initialized.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_ENV") == "development")
