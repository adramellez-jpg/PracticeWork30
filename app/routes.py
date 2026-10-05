from datetime import datetime

from flask import Blueprint, jsonify, request

from .models import Client, ClientParking, Parking, db

bp = Blueprint("api", __name__)


# ---------- Клиенты ----------


@bp.route("/clients", methods=["GET"])
def get_clients():
    """GET /clients — краткий список всех клиентов."""
    clients = (
        db.session.execute(db.select(Client).order_by(Client.id))
        .scalars()
        .all()
    )
    return jsonify(
        [{"id": c.id, "name": c.name, "surname": c.surname} for c in clients]
    )


@bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    """GET /clients/<id> — подробная информация о клиенте."""
    client = db.session.get(Client, client_id)
    if client is None:
        return jsonify(error=f"Клиент с id={client_id} не найден"), 404

    return jsonify(
        id=client.id,
        name=client.name,
        surname=client.surname,
        credit_card=client.credit_card,
        car_number=client.car_number,
    )


@bp.route("/clients", methods=["POST"])
def create_client():
    """POST /clients — создать клиента."""
    payload = request.get_json(silent=True) or {}

    required_fields = ["name", "surname", "car_number"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return jsonify(error=f"Обязательные поля: {', '.join(missing)}"), 400

    client = Client(
        name=payload["name"],
        surname=payload["surname"],
        credit_card=payload.get("credit_card"),
        car_number=payload["car_number"],
    )
    db.session.add(client)
    db.session.commit()

    return (
        jsonify(
            id=client.id,
            name=client.name,
            surname=client.surname,
            credit_card=client.credit_card,
            car_number=client.car_number,
        ),
        201,
    )


# ---------- Парковки ----------


@bp.route("/parkings", methods=["POST"])
def create_parking():
    """POST /parkings — создать парковочную зону."""
    payload = request.get_json(silent=True) or {}

    required_fields = ["address", "count_places"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return jsonify(error=f"Обязательные поля: {', '.join(missing)}"), 400

    count_places = payload["count_places"]
    if not isinstance(count_places, int) or count_places <= 0:
        return (
            jsonify(
                error="Количество парковочных мест "
                "должно быть числом больше нуля"
            ),
            400,
        )

    parking = Parking(
        address=payload["address"],
        opened=True,
        count_places=count_places,
        count_available_places=count_places,
    )
    db.session.add(parking)
    db.session.commit()

    return (
        jsonify(
            id=parking.id,
            address=parking.address,
            opened=parking.opened,
            count_places=parking.count_places,
            count_available_places=parking.count_available_places,
        ),
        201,
    )


# ---------- Заезд / Выезд ----------


@bp.route("/client_parkings", methods=["POST"])
def client_parking_in():
    """POST /client_parkings — заезд на парковку."""
    payload = request.get_json(silent=True) or {}
    client_id = payload.get("client_id")
    parking_id = payload.get("parking_id")

    if client_id is None or parking_id is None:
        return jsonify(error="Поля client_id и parking_id обязательны."), 400

    client = db.session.get(Client, client_id)
    if client is None:
        return jsonify(error=f"Клиент с id={client_id} не найден."), 404

    parking = db.session.get(Parking, parking_id)
    if parking is None:
        return jsonify(error=f"Парковка с id={parking_id} не найдена."), 404

    if not parking.opened:
        return jsonify(error="Парковка закрыта"), 403

    if parking.count_available_places <= 0:
        return jsonify(error="Свободных мест нет."), 409

    existing_parking = db.session.execute(
        db.select(ClientParking).where(
            ClientParking.client_id == client.id,
            ClientParking.parking_id == parking.id,
            ClientParking.time_out.is_(None),
        )
    ).scalar_one_or_none()
    if existing_parking is not None:
        return jsonify(error="Клиент уже на этой парковке"), 409

    parking.count_available_places -= 1

    cp = ClientParking(
        client_id=client.id,
        parking_id=parking.id,
        time_in=datetime.now(),
    )
    db.session.add(cp)
    db.session.commit()

    return (
        jsonify(
            id=cp.id,
            client_id=cp.client_id,
            parking_id=cp.parking_id,
            time_in=cp.time_in.isoformat(),
        ),
        201,
    )


@bp.route("/client_parkings", methods=["DELETE"])
def client_parking_out():
    """DELETE /client_parkings — выезд с парковки."""
    payload = request.get_json(silent=True) or {}
    client_id = payload.get("client_id")
    parking_id = payload.get("parking_id")

    if client_id is None or parking_id is None:
        return jsonify(error="Поля client_id и parking_id обязательны."), 400

    cp = db.session.execute(
        db.select(ClientParking).where(
            ClientParking.client_id == client_id,
            ClientParking.parking_id == parking_id,
            ClientParking.time_out.is_(None),
        )
    ).scalar_one_or_none()
    if cp is None:
        return jsonify(error="Активная запись парковки не найдена."), 404

    client = db.session.get(Client, client_id)
    if client is None:
        return jsonify(error=f"Клиент с id={client_id} не найден."), 404

    if not client.credit_card:
        return jsonify(error="У клиента не привязана карта"), 403

    parking = db.session.get(Parking, parking_id)
    if parking is None:
        return jsonify(error=f"Парковка с id={parking_id} не найдена."), 404

    cp.time_out = datetime.now()
    parking.count_available_places += 1

    duration_parking = int((cp.time_out - cp.time_in).total_seconds() // 60)

    db.session.commit()

    return jsonify(
        client_id=cp.client_id,
        parking_id=cp.parking_id,
        time_in=cp.time_in.isoformat(),
        time_out=cp.time_out.isoformat(),
        duration_parking_min=duration_parking,
    )
