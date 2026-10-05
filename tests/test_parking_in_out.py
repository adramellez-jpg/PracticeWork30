"""Тесты заезда и выезда с парковки."""

import pytest

from app.models import Parking


@pytest.mark.parking
def test_parking_in(client, db_session):
    """Заезд: 201, time_in заполнен, count_available_places уменьшается."""
    parking_before = db_session.get(Parking, 1)
    places_before = parking_before.count_available_places

    response = client.post(
        "/client_parkings", json={"client_id": 1, "parking_id": 1}
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["client_id"] == 1
    assert body["parking_id"] == 1
    assert body["time_in"] is not None

    parking_after = db_session.get(Parking, 1)
    places_after = parking_after.count_available_places
    assert places_before - 1 == places_after


@pytest.mark.parking
def test_parking_out(client, db_session):
    """
    Выезд: 200, time_out >= time_in, count_available_places увеличивается.
    """

    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    parking_before = db_session.get(Parking, 1)
    places_before = parking_before.count_available_places

    response = client.delete(
        "/client_parkings", json={"client_id": 1, "parking_id": 1}
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["client_id"] == 1
    assert body["parking_id"] == 1
    assert body["time_in"] is not None
    assert body["time_out"] is not None
    assert body["time_out"] >= body["time_in"]
    assert "duration_parking_min" in body

    parking_after = db_session.get(Parking, 1)
    places_after = parking_after.count_available_places
    assert places_before + 1 == places_after


@pytest.mark.parking
def test_parking_in_closed(client):
    """Заезд на закрытую парковку → 403."""
    response = client.post(
        "/client_parkings", json={"client_id": 1, "parking_id": 2}
    )

    assert response.status_code == 403
    assert "закрыта" in response.get_json()["error"].lower()


@pytest.mark.parking
def test_parking_in_no_places(client, db_session):
    """Заезд, когда нет свободных мест → 409."""
    parking = db_session.get(Parking, 1)
    parking.count_available_places = 0
    db_session.commit()

    response = client.post(
        "/client_parkings", json={"client_id": 1, "parking_id": 1}
    )

    assert response.status_code == 409
    assert "мест" in response.get_json()["error"].lower()


@pytest.mark.parking
def test_parking_out_no_card(client):
    """Выезд без привязанной карты → 403."""
    client.post("/client_parkings", json={"client_id": 2, "parking_id": 1})
    response = client.delete(
        "/client_parkings", json={"client_id": 2, "parking_id": 1}
    )

    assert response.status_code == 403
    assert "карт" in response.get_json()["error"].lower()


@pytest.mark.parking
def test_parking_in_already_parked(client):
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    response = client.post(
        "/client_parkings", json={"client_id": 1, "parking_id": 1}
    )

    assert response.status_code == 409
    assert "уже" in response.get_json()["error"].lower()
