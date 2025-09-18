from sqlalchemy.orm import Session
from decimal import Decimal

from backend.api.v1.infrastructure.db.repositories import OrderRepository, ProductRepository, OrderItemRepository
from backend.api.v1.infrastructure.db.models import OrderItem
from backend.api.v1.application.exceptions import OrderNotFound, ProductNotFound, NotEnoughStock

class AddToOrderService:
    """
    Сервис добавления товара в заказ.
    Логика:
    - Найти заказ
    - Найти товар
    - Проверить доступный остаток
    - Если позиция уже есть — увеличить количество (и зарезервировать товар)
      иначе создать новую позицию.
    - Обновить количество на складе (уменьшить).
    """

    def __init__(self, session: Session):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.product_repo = ProductRepository(session)
        self.order_item_repo = OrderItemRepository(session)

    def execute(self, order_id: int, product_id: int, quantity: int) -> OrderItem:
        # Транзакция на уровне сессии
        with self.session.begin():
            order = self.order_repo.get_by_id(order_id)
            if order is None:
                raise OrderNotFound(f"Order {order_id} not found")

            product = self.product_repo.get_by_id(product_id)
            if product is None:
                raise ProductNotFound(f"Product {product_id} not found")

            if product.quantity < quantity:
                raise NotEnoughStock(f"Not enough stock for product {product_id}")

            item = self.order_item_repo.find_by_order_and_product(order_id, product_id)

            if item:
                # проверим, что суммарно не превысим склад
                # Мы зарезервируем только запрошенное количество (уменьшим склад на quantity)
                item.quantity = int(item.quantity) + int(quantity)
                # price остается прежней (цена при добавлении первой позиции),
                self.order_item_repo.save(item)
            else:
                item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=product.price)
                self.order_item_repo.create(item)

            # уменьшение доступного количества на складе
            product.quantity = int(product.quantity) - int(quantity)
            self.product_repo.save(product)

            # session commits on exit from begin()
            return item