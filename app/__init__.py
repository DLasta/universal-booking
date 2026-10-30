
from flask import Flask

from config import Config
from app.extensions import db, migrate, login_manager
from app import models
from app.auth import auth


@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return db.session.get(models.User, user_id)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(auth)

    @app.route("/")
    def home():
        return "Universal Booking is running!"

    return app
