import os


class Config:
    """Конфигурация Flask-приложения."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///parking.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False