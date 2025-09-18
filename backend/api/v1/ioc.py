from functools import lru_cache
from fastapi import Depends
from backend.api.v1.infrastructure.db.database import SessionLocal, engine
from backend.api.v1.infrastructure.db import models as db_models
from backend.api.v1.application.services import AddToOrderService

# Простая инициализация БД (создаёт таблицы при старте если их нет)
def init_db():
    db_models.Base.metadata.create_all(bind=engine)

# Минимальный IoC / фабрика для сервиса
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Фабрика провайдера сервиса, совместимая с FastAPI Depends
def get_add_to_order_service(db = Depends(get_db_session)):
    # Возвращаем объект сервиса, привязанный к сессии
    return AddToOrderService(db)