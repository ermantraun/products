import pytest
from decimal import Decimal

from backend.api.v1.infrastructure.db.database import engine, SessionLocal
from backend.api.v1.infrastructure.db import models
from backend.api.v1.application.services import AddToOrderService
from backend.api.v1.application.exceptions import NotEnoughStock, OrderNotFound, ProductNotFound

# Используем отдельную БД (файл sqlite) — таблицы создаются заново
@pytest.fixture(scope="function")
def setup_db():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Создадим клиента, заказ и продукт
        client = models.Client(name="Test Client")
        session.add(client)
        session.flush()
        order = models.Order(client_id=client.id)
        session.add(order)
        session.flush()
        product = models.Product(name="Widget", quantity=10, price=Decimal("9.99"))
        session.add(product)
        session.commit()
        yield {
            "session": session,
            "client": client,
            "order": order,
            "product": product
        }
    finally:
        session.close()

def test_add_new_item(setup_db):
    session = SessionLocal()
    service = AddToOrderService(session)
    order_id = setup_db["order"].id
    product_id = setup_db["product"].id

    item = service.execute(order_id=order_id, product_id=product_id, quantity=3)
    assert item.quantity == 3
    # product quantity decreased
    p = session.get(models.Product, product_id)
    assert p.quantity == 7
    session.close()

def test_increase_existing_item(setup_db):
    session = SessionLocal()
    service = AddToOrderService(session)
    order_id = setup_db["order"].id
    product_id = setup_db["product"].id

    # first add 2
    item1 = service.execute(order_id=order_id, product_id=product_id, quantity=2)
    # then add 4 more
    item2 = service.execute(order_id=order_id, product_id=product_id, quantity=4)
    assert item2.id == item1.id or item2.order_id == order_id
    assert item2.quantity == 6
    p = session.get(models.Product, product_id)
    assert p.quantity == 4
    session.close()

def test_not_enough_stock(setup_db):
    session = SessionLocal()
    service = AddToOrderService(session)
    order_id = setup_db["order"].id
    product_id = setup_db["product"].id

    with pytest.raises(NotEnoughStock):
        service.execute(order_id=order_id, product_id=product_id, quantity=100)
    session.close()

def test_order_not_found(setup_db):
    session = SessionLocal()
    service = AddToOrderService(session)
    with pytest.raises(OrderNotFound):
        service.execute(order_id=9999, product_id=setup_db["product"].id, quantity=1)
    session.close()

def test_product_not_found(setup_db):
    session = SessionLocal()
    service = AddToOrderService(session)
    with pytest.raises(ProductNotFound):
        service.execute(order_id=setup_db["order"].id, product_id=9999, quantity=1)
    session.close()