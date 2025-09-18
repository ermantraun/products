```markdown
# 3. Сервис «Добавление товара в заказ»

## 🚀 Технологии

- FastAPI — асинхронный веб-фреймворк для создания REST API
- SQLAlchemy — ORM
- Pydantic — DTO/валидация
- Dishka-like IoC (простой провайдер через FastAPI Depends)
- PostgreSQL — база данных в продакшн/через docker-compose
- Pytest — тестирование
- Docker / docker-compose — контейнеризация

---

## 📁 Структура проекта

```bash
project/
├── backend/
│   └── api/
│       └── v1/
│           ├── handlers/
│           ├── application/
│           ├── domen/
│           ├── infrastructure/
│           │   └── db/
│           ├── ioc.py
│           ├── main.py
│           └── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙ Конфигурация и переменные окружения

Приложение читает DATABASE_URL из окружения. Пример значения для docker-compose:

DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/app_db

Если вы запускаете локально без Postgres, по умолчанию используется SQLite:
DATABASE_URL по умолчанию: sqlite:///./test.db

Рекомендуется в requirements.txt иметь psycopg2-binary для работы с Postgres в контейнере:
- psycopg2-binary

---

## 🐳 Docker и docker-compose

В проекте есть docker-compose.yml для полноценного разворачивания:

- Сервис db: Postgres (named volume для долговременного хранения)
- Сервис web: приложение на FastAPI (uvicorn)
- Сервис pgadmin: визуальная панель для работы с БД (опционально)

Команды:

1) Собрать и поднять все сервисы:
   docker compose up --build -d

2) Посмотреть логи приложения:
   docker compose logs -f web

3) Остановить и удалить контейнеры и тома данных:
   docker compose down -v

Важно:
- В docker-compose в переменной окружения web передаётся DATABASE_URL, например:
  postgresql+psycopg2://postgres:postgres@db:5432/app_db
- Убедитесь, что в requirements.txt есть psycopg2-binary или в Dockerfile установлены необходимые пакеты для сборки psycopg2.
- В Dockerfile можно оставить команду запуска uvicorn; web контейнер ждёт доступности БД через depends_on + healthcheck.

---

## 🚀 Локальный запуск (без docker)

1) Создать виртуальное окружение и установить зависимости:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2) Запустить приложение (по умолчанию SQLite если не задано DATABASE_URL):
   uvicorn backend.api.v1.main:app --reload

---

## 🧪 Тестирование

Запуск тестов локально:
   pytest -q

В контейнере (если нужно выполнить в web контейнере):
   docker compose exec web pytest -q

---

## 📦 API

POST /orders/{order_id}/items
- body: {"product_id": int, "quantity": int}
- Ответы:
  - 200 — товар добавлен/обновлён (возвращается позиция заказа)
  - 404 — заказ или товар не найден
  - 400 — недостаточно товара на складе

Пример curl:
curl -X POST "http://127.0.0.1:8000/orders/1/items" -H "Content-Type: application/json" -d '{"product_id":1,"quantity":2}'

---

## 🧭 Примечания и рекомендации

- CI / Production:
  - Рекомендую настроить миграции Alembic для управления схемой БД.
  - Для продакшна используйте отдельный процесс сборки Docker image и не монтируйте код через volumes.
- Dockerfile:
  - Если используете psycopg2-binary — достаточно добавить его в requirements.txt.
  - Если используете psycopg2 (не-binary) — потребуется установить системные зависимости (libpq-dev, build-essential).
- Инициализация БД:
  - В текущем примере таблицы создаются через db_models.Base.metadata.create_all(bind=engine) на старте приложения (ioc.init_db).

---

Спасибо — я адаптировал README под docker-compose, добавил инструкции по запуску, окружению и примечания по зависимостям. Если хотите, могу сразу:
- показать обновлённый Dockerfile и requirements.txt с psycopg2-binary,
- либо добавить небольшой entrypoint-скрипт для ожидания готовности БД перед запуском uvicorn.
```