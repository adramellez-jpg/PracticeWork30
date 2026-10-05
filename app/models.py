from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Client(db.Model):
    """Клиент парковки: имя, фамилия, карта, номер авто."""

    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    surname: Mapped[str] = mapped_column(db.String(50), nullable=False)
    credit_card: Mapped[str | None] = mapped_column(
        db.String(50), nullable=True
    )
    car_number: Mapped[str] = mapped_column(db.String(10), nullable=False)

    client_parkings: Mapped[list["ClientParking"]] = db.relationship(
        back_populates="client"
    )


class Parking(db.Model):
    """Парковка: адрес, статус, общее и доступное число мест."""

    __tablename__ = "parking"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(db.String(100), nullable=False)
    opened: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    count_places: Mapped[int] = mapped_column(db.Integer, nullable=False)
    count_available_places: Mapped[int] = mapped_column(
        db.Integer, nullable=False
    )

    client_parkings: Mapped[list["ClientParking"]] = db.relationship(
        back_populates="parking"
    )


class ClientParking(db.Model):
    """Лог въезда-выезда: клиент, парковка, время входа и выхода."""

    __tablename__ = "client_parking"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        db.ForeignKey("client.id"), nullable=False
    )
    parking_id: Mapped[int] = mapped_column(
        db.ForeignKey("parking.id"), nullable=False
    )
    time_in: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    time_out: Mapped[datetime | None] = mapped_column(
        db.DateTime, nullable=True
    )

    client: Mapped["Client"] = db.relationship(
        back_populates="client_parkings"
    )
    parking: Mapped["Parking"] = db.relationship(
        back_populates="client_parkings"
    )
