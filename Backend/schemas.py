from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True
        

class VendorCreate(BaseModel):
    restaurant_name: str
    description: str
        

class VendorResponse(BaseModel):
    id: int
    restaurant_name: str
    description: str
    owner_id: int

    class Config:
        from_attributes = True
        

class FoodCreate(BaseModel):
    name: str
    price: float
        

class FoodResponse(BaseModel):
    id: int
    name: str
    price: float
    vendor_id: int

    class Config:
        from_attributes = True
        

class CartItemCreate(BaseModel):
    food_id: int
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    food_id: int
    quantity: int
    food: Optional[FoodResponse] = None
    
    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    id: int
    food_id: int
    quantity: int
    unit_price: float
    food: Optional[FoodResponse] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    vendor_id: int
    total_price: float


class OrderResponse(BaseModel):
    id: int
    user_id: int
    vendor_id: int
    total_price: float
    status: str
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True