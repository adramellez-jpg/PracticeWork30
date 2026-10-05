from flask import Flask

from .config import Config
from .models import db
from .routes import bp


def create_app(config_class: type = Config) -> Flask:
    """Фабрика Flask-приложения."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(bp)

    return app
