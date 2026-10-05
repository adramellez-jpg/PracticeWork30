"""Фабрики для генерации тестовых данных через Factory Boy + Faker."""

import random

import factory
from faker import Faker

from app.models import Client, Parking, db

fake = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика клиента: name/surname из Faker, карта — рандомно есть/нет."""

    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.LazyFunction(lambda: fake.credit_card_number() if random.choice([True, False]) else None)
    car_number = factory.Faker("bothify", text="?####??")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика парковки: адрес из Faker, места — count_available = count_places."""

    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    address = factory.Faker("address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=5, max=50)
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)
