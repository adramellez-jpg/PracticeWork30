"""Фикстуры для тестов."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.pool import StaticPool

from app import create_app
from app.config import Config
from app.models import Client, ClientParking, Parking, db


class TestConfig(Config):
    """Конфиг для тестов: SQLite в памяти."""

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    }


@pytest.fixture
def app():
    """Создаёт приложение с тестовой БД и начальными данными."""
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        # тестовый клиент
        client = Client(
            name="Иван",
            surname="Иванов",
            credit_card="1234 5678 9012 3456",
            car_number="A123BC",
        )
        # клиент без карты — для проверки отказа при оплате
        client_no_card = Client(
            name="Пётр",
            surname="Петров",
            credit_card=None,
            car_number="B456CD",
        )
        # тестовая парковка
        parking = Parking(
            address="ул. Ленина 1",
            opened=True,
            count_places=10,
            count_available_places=10,
        )
        # закрытая парковка — для проверки отказа при заезде
        parking_closed = Parking(
            address="ул. Закрытая 1",
            opened=False,
            count_places=5,
            count_available_places=5,
        )

        db.session.add_all([client, client_no_card, parking, parking_closed])
        db.session.commit()

        # завершённая поездка (time_in + time_out)
        now = datetime.now()
        finished_parking = ClientParking(
            client_id=client.id,
            parking_id=parking.id,
            time_in=now - timedelta(hours=2),
            time_out=now - timedelta(hours=1),
        )
        db.session.add(finished_parking)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client для запросов к приложению."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Сессия БД для проверок внутри тестов."""
    with app.app_context():
        yield db.session
