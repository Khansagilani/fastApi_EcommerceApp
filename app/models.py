from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ── Users ────────────────────────────────────────────────────────────────────

class UserBase(SQLModel):
    name: str
    email: str = Field(unique=True, index=True)
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    is_admin: bool = False


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


# ── Products ─────────────────────────────────────────────────────────────────

class ProductBase(SQLModel):
    product_name: str = Field(index=True)
    Product_Description: Optional[str] = None
    price: Decimal = Field(decimal_places=2, max_digits=10)
    quantity: int = Field(default=0)
    img: Optional[str] = None


class Product(ProductBase, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    created_at: datetime


class ProductUpdate(SQLModel):
    product_name: Optional[str] = None
    Product_Description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    img: Optional[str] = None
# ── Carts ────────────────────────────────────────────────────────────────────


class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Cart Items ────────────────────────────────────────────────────────────────

class CartItemBase(SQLModel):
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(default=1, ge=1)


class CartItem(CartItemBase, table=True):
    __tablename__ = "cart_items"
    id: Optional[int] = Field(default=None, primary_key=True)


class CartItemCreate(SQLModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(SQLModel):
    quantity: int = Field(ge=1)


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderBase(SQLModel):
    user_id: int = Field(foreign_key="users.id")
    total_amount: Decimal = Field(decimal_places=2, max_digits=12)
    # pending | paid | shipped | delivered
    status: str = Field(default="pending")
    shipping_addr: Optional[str] = None


class Order(OrderBase, table=True):
    __tablename__ = "orders"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrderRead(OrderBase):
    id: int
    created_at: datetime


# ── Order Items ───────────────────────────────────────────────────────────────

class OrderItemBase(SQLModel):
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int
    # snapshot at time of order
    price: Decimal = Field(decimal_places=2, max_digits=10)


class OrderItem(OrderItemBase, table=True):
    __tablename__ = "order_items"
    id: Optional[int] = Field(default=None, primary_key=True)
