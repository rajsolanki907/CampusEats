from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base 


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    cart_items = relationship("CartItem", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String, unique=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    orders = relationship("Order", back_populates="restaurant")


class FoodItem(Base):
    __tablename__ = "food_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("food_items.id"))
    quantity = Column(Integer, default=1)

    customer = relationship("User", back_populates="cart_items")
    food = relationship("FoodItem")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    total_price = Column(Float)
    status = Column(String, default="Pending")  # e.g., Pending, Accepted, Delivered

    customer = relationship("User", back_populates="orders")
    restaurant = relationship("Vendor", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    food_id = Column(Integer, ForeignKey("food_items.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)

    order = relationship("Order", back_populates="items")
    food = relationship("FoodItem")