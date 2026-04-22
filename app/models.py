from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import EmailStr

# ── Users ────────────────────────────────────────────────────────────────────


class UserBase(SQLModel):
    name: str
    email: EmailStr = Field(unique=True, index=True)
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None


class User(UserBase, table=True):
    __tablename__ = "users"
    is_admin: bool = False
    orders: list["Order"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    carts: list["Cart"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    orders: list["Order"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


# ── Products ─────────────────────────────────────────────────────────────────

class ProductBase(SQLModel):
    product_name: str = Field(index=True)
    product_Description: Optional[str] = None
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
    product_Description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    img: Optional[str] = None
# ── Carts ────────────────────────────────────────────────────────────────────


class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="carts")

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
    user: Optional["User"] = Relationship(back_populates="orders")


class OrderRead(OrderBase):
    id: int
    created_at: datetime


class CheckoutRequest(SQLModel):
    shipping_addr: str


class StatusUpdate(SQLModel):
    status: str

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
