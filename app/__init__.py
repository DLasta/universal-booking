
from flask import Flask

from config import Config
from app.extensions import db, migrate
from app import models
from app.auth import auth


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth)

    @app.route("/")
    def home():
        return "Universal Booking is running!"

    return app
