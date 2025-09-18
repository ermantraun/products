from sqlalchemy.orm import Session
from .models import Order, Product, OrderItem
from typing import Optional

class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.session.get(Order, order_id)

    def save(self, order: Order):
        self.session.add(order)

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)

    def save(self, product: Product):
        self.session.add(product)

class OrderItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_order_and_product(self, order_id: int, product_id: int) -> Optional[OrderItem]:
        return self.session.query(OrderItem).filter_by(order_id=order_id, product_id=product_id).one_or_none()

    def create(self, order_item: OrderItem):
        self.session.add(order_item)

    def save(self, order_item: OrderItem):
        self.session.add(order_item)