# 1. Спроектировать схему БД.

<img width="769" height="517" alt="image" src="https://github.com/user-attachments/assets/c5560ae8-0495-45ee-8ac7-b687f12bf7de" />

# 2. Написать SQL запросы

2.1. Сумма по клиентам (наименование клиента, сумма в валюте)
````sql
SELECT
  c.name AS client_name,
  COALESCE(SUM(oi.quantity * oi.price), 0) AS total_amount
FROM clients c
LEFT JOIN orders o ON o.client_id = c.id
LEFT JOIN order_items oi ON oi.order_id = o.id
GROUP BY c.id, c.name
ORDER BY total_amount DESC;
````

2.2. Количество дочерних элементов первого уровня для категорий
````sql
SELECT
  c.id,
  c.name,
  COUNT(ch.id) AS children_count
FROM categories c
LEFT JOIN categories ch ON ch.parent_id = c.id
GROUP BY c.id, c.name
ORDER BY children_count DESC;
````

2.3.1. Топ‑5 самых покупаемых товаров за последний месяц (по количеству штук), с категорией 1-го уровня (root‑категория)
- используем рекурсивный CTE, чтобы найти корневую категорию (parent_id IS NULL) для каждой категории
````sql
CREATE OR REPLACE VIEW top_5_products_last_month AS
WITH RECURSIVE cat_root AS (
  SELECT id, name, parent_id, id AS root_id, name AS root_name
  FROM categories
  WHERE parent_id IS NULL

  UNION ALL

  SELECT c.id, c.name, c.parent_id, cr.root_id, cr.root_name
  FROM categories c
  JOIN cat_root cr ON c.parent_id = cr.id
)
SELECT
  p.id    AS product_id,
  p.name  AS product_name,
  cr.root_name AS category_level_1,
  SUM(oi.quantity) AS total_quantity_sold
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
LEFT JOIN (
  -- для каждой категории выбираем её корневую категорию (если категория NULL — NULL)
  SELECT id, root_id, root_name FROM (
    SELECT c.id, cr.root_id, cr.root_name,
           ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY cr.root_id) rn
    FROM categories c
    LEFT JOIN cat_root cr ON c.id = cr.id OR c.parent_id = cr.id
  ) t WHERE rn = 1
) cr_map ON p.category_id = cr_map.id
LEFT JOIN categories cr ON cr.id = cr_map.root_id
WHERE o.created_at >= now() - INTERVAL '1 month'
GROUP BY p.id, p.name, cr.root_name
ORDER BY total_quantity_sold DESC
LIMIT 5;
````

2.3.2. Анализ и варианты оптимизации (кратко)

- Индексы (первые шаги)
  - orders(created_at) — ускорит поиск по периоду
  - order_items(product_id), order_items(order_id) — ускорят агрегации и JOIN
  - products(category_id) и categories(parent_id)
  Примеры:
  ```sql
  CREATE INDEX ON orders (created_at);
  CREATE INDEX ON order_items (product_id);
  CREATE INDEX ON order_items (order_id);
  CREATE INDEX ON products (category_id);
  CREATE INDEX ON categories (parent_id);
  ```

- Уменьшить число JOIN-ов
  - Денормализовать: в таблицу products добавить колонку root_category_id (или category_level_1_id) и поддерживать её при изменении категорий. Тогда запрос избегает рекурсивного обхода.
  - Добавить индекс products(root_category_id).

- Материализованный/инкрементный предрасчёт
  - Создать материализованный view или отдельную таблицу agg_product_sales(product_id, period_start, total_qty) и обновлять её по расписанию (refresh materialized view) или поддерживать через триггеры/фоновые таски при создании заказов.
  - Пример materialized view:
    ```sql
    CREATE MATERIALIZED VIEW mv_product_monthly_sales AS
    SELECT p.id AS product_id, date_trunc('month', o.created_at) AS month, SUM(oi.quantity) total_qty
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    JOIN products p ON oi.product_id = p.id
    GROUP BY p.id, date_trunc('month', o.created_at);
    ```
    Затем для топ‑5 — запрос к mv_product_monthly_sales для текущего месяца с JOIN по products и категориям.

- Партиционирование
  - Партиционировать таблицы orders и/или order_items по времени.


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
