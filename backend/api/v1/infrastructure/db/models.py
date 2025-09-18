import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime
from decimal import Decimal
from typing import Optional

class Base(sa.orm.DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        sa.Index("ix_categories_name", "name"),
        sa.Index("ix_categories_parent_id", "parent_id"),
    )

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(sa.String(length=255), nullable=False)
    parent_id: Optional[int] = sa.Column(sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    parent = orm.relationship("Category", remote_side=[id], back_populates="children", uselist=False)
    children = orm.relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = orm.relationship("Product", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, parent_id={self.parent_id})>"

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        sa.Index("ix_products_name", "name"),
        sa.Index("ix_products_category_id", "category_id"),
    )

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(sa.String(length=255), nullable=False)
    quantity: int = sa.Column(sa.Integer, nullable=False, default=0)
    price: Decimal = sa.Column(sa.Numeric(12, 2), nullable=False, default=0)
    category_id: Optional[int] = sa.Column(sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    category = orm.relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, qty={self.quantity}, price={self.price})>"

class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        sa.Index("ix_clients_name", "name"),
    )

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(sa.String(length=255), nullable=False)
    address: Optional[str] = sa.Column(sa.String(length=1024), nullable=True)

    orders = orm.relationship("Order", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name})>"

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        sa.Index("ix_orders_client_id", "client_id"),
    )

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    client_id: int = sa.Column(sa.Integer, sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    created_at: datetime = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status: str = sa.Column(sa.String(length=50), nullable=False, default="new")

    client = orm.relationship("Client", back_populates="orders")
    items = orm.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, client_id={self.client_id}, status={self.status})>"

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        sa.Index("ix_order_items_order_id", "order_id"),
        sa.Index("ix_order_items_product_id", "product_id"),
    )

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    order_id: int = sa.Column(sa.Integer, sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: int = sa.Column(sa.Integer, sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    quantity: int = sa.Column(sa.Integer, nullable=False, default=1)
    price: Decimal = sa.Column(sa.Numeric(12, 2), nullable=False, default=0) 

    order = orm.relationship("Order", back_populates="items")
    product = orm.relationship("Product")

    def line_total(self) -> Decimal:
        return Decimal(self.quantity) * Decimal(self.price)

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"