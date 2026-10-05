"""Тесты эндпоинтов парковок."""

from app.models import Parking

from .factories import ParkingFactory


def test_create_parking(client):
    """POST /parkings создаёт парковку: opened=True, все места свободны."""

    payload = {
        "address": "Mars, Olympus",
        "count_places": 10,
    }
    response = client.post("/parkings", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["address"] == "Mars, Olympus"
    assert body["opened"] is True
    assert body["count_places"] == 10
    assert body["count_available_places"] == 10


def test_create_parking_factory(client, db_session):
    """ParkingFactory создаёт запись в БД: проверяем id, число строк, места."""
    parkings_before = db_session.query(Parking).count()

    fake_parking = ParkingFactory()

    assert fake_parking.id is not None
    assert fake_parking.count_available_places == fake_parking.count_places
    assert db_session.query(Parking).count() == parkings_before + 1
