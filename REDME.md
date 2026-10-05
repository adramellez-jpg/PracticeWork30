# Parking API

Flask-приложение для сервиса оплаты парковки: клиенты, парковочные зоны, лог въезда-выезда.

Когда автомобиль подъезжает к парковке, камера считывает номер, и — если есть свободные места — шлагбаум поднимается.
При выезде фиксируется время, списываются средства с привязанной карты.

## Стек

- **Flask** 3.1.3 — веб-фреймворк
- **Flask-SQLAlchemy** 3.1.1 — ORM-обёртка над SQLAlchemy
- **SQLAlchemy** 2.1.1 — ORM
- **SQLite** — база данных
- **pytest** 9.1.1 — тесты
- **factory-boy** 3.3.3 + **Faker** 40.40.0 — генерация тестовых данных

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python run.py
```

Приложение стартует на http://localhost:5000 (dev-сервер Flask).

При первом запуске создаётся файл `instance/parking.db` — таблицы будут созданы автоматически.

## Эндпоинты

| Метод  | Путь               | Что делает                                  |
|--------|--------------------|---------------------------------------------|
| GET    | `/clients`         | Краткий список клиентов (id, name, surname) |
| GET    | `/clients/<id>`    | Подробная информация о клиенте              |
| POST   | `/clients`         | Создать нового клиента                      |
| POST   | `/parkings`        | Создать парковочную зону                    |
| POST   | `/client_parkings` | Заезд на парковку                           |
| DELETE | `/client_parkings` | Выезд с парковки                            |

### Примеры запросов

**Создать клиента:**

```bash
curl -X POST http://localhost:5000/clients \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Иван",
    "surname": "Иванов",
    "credit_card": "1234 5678 9012 3456",
    "car_number": "A123BC"
  }'
```

**Создать парковку:**

```bash
curl -X POST http://localhost:5000/parkings \
  -H 'Content-Type: application/json' \
  -d '{
    "address": "ул. Ленина 1",
    "count_places": 10
  }'
```

**Заехать на парковку:**

```bash
curl -X POST http://localhost:5000/client_parkings \
  -H 'Content-Type: application/json' \
  -d '{"client_id": 1, "parking_id": 1}'
```

**Выехать с парковки:**

```bash
curl -X DELETE http://localhost:5000/client_parkings \
  -H 'Content-Type: application/json' \
  -d '{"client_id": 1, "parking_id": 1}'
```

## Тесты

```bash
# Все тесты
pytest -v

# Только тесты заезда/выезда (маркер parking)
pytest -v -m parking
```

Покрытие: 12 тестов.

- **GET-эндпоинты** — параметризованный тест на 200;
- **Создание клиента** — обычный тест и через `ClientFactory`;
- **Создание парковки** — обычный тест и через `ParkingFactory`;
- **Заезд/выезд** (маркер `parking`):
    - успешный заезд — `time_in` заполнен, `count_available_places` уменьшается;
    - успешный выезд — `time_out >= time_in`, `count_available_places` увеличивается;
    - заезд на закрытую парковку → 403;
    - заезд при отсутствии мест → 409;
    - выезд без привязанной карты → 403;
    - повторный заезд без выезда → 409.

### Фикстуры

В `tests/conftest.py`:

- **`app`** — приложение с in-memory SQLite и тестовыми данными (клиент, парковка, лог);
- **`client`** — Flask test client;
- **`db_session`** — сессия БД для проверок в тестах.

### Фабрики

В `tests/factories.py`:

- **`ClientFactory`** — `name`/`surname` через Faker, `credit_card` рандомно (есть/нет), `car_number` через `bothify`;
- **`ParkingFactory`** — адрес из Faker, `opened` — boolean, `count_places` — int,
  `count_available_places = count_places` через `LazyAttribute`.

## Структура проекта

```
hw/
├── app/
│   ├── __init__.py         # create_app() — Application Factory
│   ├── config.py           # конфигурация Flask + БД
│   ├── models.py           # db + Client, Parking, ClientParking
│   └── routes.py           # Blueprint + 6 роутов
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # фикстуры app, client, db_session
│   ├── factories.py        # ClientFactory, ParkingFactory
│   ├── test_get.py         # параметризованные GET-тесты
│   ├── test_clients.py     # тесты клиентов
│   ├── test_parkings.py    # тесты парковок
│   └── test_parking_in_out.py  # заезд/выезд (маркер parking)
├── instance/
│   └── parking.db          # SQLite (создаётся автоматически)
├── pytest.ini              # конфиг pytest + маркер parking
├── requirements.txt
├── run.py                  # точка входа
└── task.md                 # задание
```

## Модели

### `Client`

| Поле          | Тип               | Описание                              |
|---------------|-------------------|---------------------------------------|
| `id`          | int, PK           | Идентификатор                         |
| `name`        | str(50)           | Имя                                   |
| `surname`     | str(50)           | Фамилия                               |
| `credit_card` | str(50), nullable | Номер карты (может быть не привязана) |
| `car_number`  | str(10)           | Номер автомобиля                      |

### `Parking`

| Поле                     | Тип      | Описание            |
|--------------------------|----------|---------------------|
| `id`                     | int, PK  | Идентификатор       |
| `address`                | str(100) | Адрес               |
| `opened`                 | bool     | Открыта ли парковка |
| `count_places`           | int      | Всего мест          |
| `count_available_places` | int      | Свободных мест      |

### `ClientParking`

| Поле         | Тип                | Описание                              |
|--------------|--------------------|---------------------------------------|
| `id`         | int, PK            | Идентификатор                         |
| `client_id`  | FK → Client        | Клиент                                |
| `parking_id` | FK → Parking       | Парковка                              |
| `time_in`    | datetime           | Время въезда                          |
| `time_out`   | datetime, nullable | Время выезда (заполняется при выезде) |

## Особенности реализации

- **`credit_card` nullable** — при регистрации карта может отсутствовать, но POST `/clients` требует её (валидация на
  уровне API).
- **`UNIQUE (client_id, parking_id)`** убран из модели — чтобы клиент мог заехать повторно после выезда. Защита от *
  *одновременного** двойного заезда — в коде (`409`, если уже на парковке).
- **`opened=True`** при создании парковки.