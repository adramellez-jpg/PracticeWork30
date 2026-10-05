"""Тесты GET-эндпоинтов."""
import pytest


@pytest.mark.parametrize("endpoint", ["/clients", "/clients/1"])
def test_get_endpoint_return_200(client, endpoint):
    """Все GET-методы возвращают код 200."""
    response = client.get(endpoint)
    assert response.status_code == 200
