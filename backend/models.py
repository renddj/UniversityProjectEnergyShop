# from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from database import Base


# class User(Base):
#     """Пользователь сайта"""
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     password_hash = Column(String(255), nullable=False)
#     # Роль: "user" — обычный пользователь, "admin" — администратор
#     role = Column(String(10), default="user", nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     # Связь: у пользователя есть корзина
#     cart_items = relationship("CartItem", back_populates="user", cascade="all, delete")


# class Product(Base):
#     """Карточка товара"""
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)           # Название
#     brand = Column(String(50), nullable=False)           # Бренд
#     price = Column(Float, nullable=False)                # Цена
#     volume = Column(String(20), nullable=False)          # Объём (например "0.5л")
#     short_description = Column(String(200), nullable=False)  # Краткое описание (для списка)
#     full_description = Column(Text, nullable=False)      # Полное описание (для страницы товара)
#     image_url = Column(String(500), nullable=False)      # Ссылка на изображение
#     in_stock = Column(Integer, default=1)                # В наличии: 1 = да, 0 = нет
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     cart_items = relationship("CartItem", back_populates="product", cascade="all, delete")


# class CartItem(Base):
#     """Элемент корзины"""
#     __tablename__ = "cart_items"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     quantity = Column(Integer, default=1, nullable=False)  # Количество

#     user = relationship("User", back_populates="cart_items")
#     product = relationship("Product", back_populates="cart_items")


from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """Пользователь сайта"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    # Роль: "user" — обычный пользователь, "admin" — администратор
    role = Column(String(10), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь: у пользователя есть корзина
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete")


class Product(Base):
    """Карточка товара"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)           # Название
    brand = Column(String(50), nullable=False)           # Бренд
    price = Column(Float, nullable=False)                # Цена
    volume = Column(String(20), nullable=False)          # Объём (например "0.5л")
    short_description = Column(String(200), nullable=False)  # Краткое описание (для списка)
    full_description = Column(Text, nullable=False)      # Полное описание (для страницы товара)
    image_url = Column(String(500), nullable=False)      # Ссылка на изображение
    in_stock = Column(Integer, default=1)                # В наличии: 1 = да, 0 = нет
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete")


class CartItem(Base):
    """Элемент корзины"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)  # Количество

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    """Заказ"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # None для гостей
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(30), nullable=False)
    customer_email = Column(String(100), nullable=False)
    delivery_method = Column(String(30), nullable=False)
    delivery_address = Column(String(300), nullable=False)
    payment_method = Column(String(30), nullable=False)
    comment = Column(Text, nullable=True)
    subtotal = Column(Float, nullable=False)
    delivery_cost = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(30), default="new", nullable=False)  # new / confirmed / shipped / delivered
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    """Позиция в заказе"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(100), nullable=False)  # копируем на случай удаления товара
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")