from fastapi import FastAPI
from backend.api.v1.handlers import orders
from backend.api.v1.ioc import init_db

app = FastAPI(title="Add item to order - example")

# Инициализация БД при старте (создаёт таблицы для SQLite/DB)
@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(orders.router)