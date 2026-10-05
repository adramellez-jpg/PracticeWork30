"""Тесты эндпоинтов клиентов."""

from app.models import Client

from .factories import ClientFactory


def test_create_client(client):
    """POST /clients создаёт клиента и возвращает 201 с его данными."""
    payload = {
        "name": "John",
        "surname": "Wick",
        "credit_card": "1111 2222 3333 4444",
        "car_number": "X666YZ",
    }
    response = client.post("/clients", json=payload)
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "John"
    assert body["surname"] == "Wick"
    assert body["credit_card"] == "1111 2222 3333 4444"
    assert body["car_number"] == "X666YZ"
    assert body["id"] == 3


def test_create_client_factory(client, db_session):
    """ClientFactory создаёт запись в БД: проверяем id, число строк и GET."""
    clients_before = db_session.query(Client).count()

    fake_client = ClientFactory()

    assert fake_client.id is not None
    assert db_session.query(Client).count() == clients_before + 1

    response = client.get(f"/clients/{fake_client.id}")
    assert response.status_code == 200
    assert response.get_json()["name"] == fake_client.name
