from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=100)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    role: str
    username: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str
    balance: float
    created_at: datetime


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = ""
    price: float = Field(ge=0)
    stock: int = Field(ge=0)


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CartAddIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemOut(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float


class TopUpIn(BaseModel):
    amount: float = Field(gt=0, le=100_000_000)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_name: str
    price: float
    quantity: int


class OrderOut(BaseModel):
    id: int
    username: str
    total: float
    created_at: datetime
    items: list[OrderItemOut]