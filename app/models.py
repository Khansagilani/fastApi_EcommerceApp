from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import EmailStr


# ── Users ─────────────────────────────────────────────────────────────────────

class UserBase(SQLModel):
    name: str
    email: EmailStr = Field(unique=True, index=True)
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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


class UserRead(SQLModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(SQLModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


# ── Products ──────────────────────────────────────────────────────────────────

class ProductBase(SQLModel):
    product_name: str = Field(index=True)
    product_Description: Optional[str] = None
    price: Decimal = Field(decimal_places=2, max_digits=10)
    quantity: int = Field(default=0)
    img: Optional[str] = None
    category: Optional[str] = Field(default=None)    # rtw, unstitched
    style: Optional[str] = Field(default=None)        # casual, formal
    pieces: Optional[str] = Field(default=None)       # 2piece, 3piece
    fabric_type: Optional[str] = Field(default=None)  # embroidered, printed
    sizes: Optional[str] = Field(default=None)        # comma-separated: "XS,S,M,L,XL"


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
    category: Optional[str] = None
    style: Optional[str] = None
    pieces: Optional[str] = None
    fabric_type: Optional[str] = None
    sizes: Optional[str] = None


# ── Carts ─────────────────────────────────────────────────────────────────────

class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="carts")


# ── Cart Items ────────────────────────────────────────────────────────────────

class CartItemBase(SQLModel):
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(default=1, ge=1)
    size: Optional[str] = None


class CartItem(CartItemBase, table=True):
    __tablename__ = "cart_items"
    id: Optional[int] = Field(default=None, primary_key=True)


class CartItemCreate(SQLModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)
    size: Optional[str] = None


class CartItemUpdate(SQLModel):
    quantity: int = Field(ge=1)


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderBase(SQLModel):
    user_id: int = Field(foreign_key="users.id")
    total_amount: Decimal = Field(decimal_places=2, max_digits=12)
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
    promo_code: Optional[str] = None


class StatusUpdate(SQLModel):
    status: str


# ── Order Items ───────────────────────────────────────────────────────────────

class OrderItemBase(SQLModel):
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int
    price: Decimal = Field(decimal_places=2, max_digits=10)
    size: Optional[str] = None


class OrderItem(OrderItemBase, table=True):
    __tablename__ = "order_items"
    id: Optional[int] = Field(default=None, primary_key=True)


class OrderItemDetail(SQLModel):
    product_id: int
    product_name: str
    product_img: Optional[str] = None
    size: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float


class OrderDetail(SQLModel):
    id: int
    status: str
    total_amount: float
    shipping_addr: Optional[str] = None
    created_at: datetime
    items: List[OrderItemDetail] = []


class OrderWithCustomer(SQLModel):
    id: int
    user_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    total_amount: float
    status: str
    shipping_addr: Optional[str] = None
    created_at: datetime


# ── Blacklisted Tokens ────────────────────────────────────────────────────────

class BlacklistedToken(SQLModel, table=True):
    __tablename__ = "blacklisted_tokens"
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True)
    blacklisted_at: datetime = Field(default_factory=datetime.utcnow)


# ── Wishlist ──────────────────────────────────────────────────────────────────

class WishlistItem(SQLModel, table=True):
    __tablename__ = "wishlist_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Reviews ───────────────────────────────────────────────────────────────────

class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = None


class Review(ReviewBase, table=True):
    __tablename__ = "reviews"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    reviewer_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int
    user_id: int
    reviewer_name: Optional[str] = None
    created_at: datetime


# ── Promo Codes ───────────────────────────────────────────────────────────────

class PromoCode(SQLModel, table=True):
    __tablename__ = "promo_codes"
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    discount_percent: int = Field(ge=1, le=100)
    active: bool = Field(default=True)
    uses_remaining: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromoCodeCreate(SQLModel):
    code: str
    discount_percent: int
    uses_remaining: Optional[int] = None


class PromoCodeRead(SQLModel):
    id: int
    code: str
    discount_percent: int
    active: bool
    uses_remaining: Optional[int] = None
    created_at: datetime


# ── Product Images ────────────────────────────────────────────────────────────

class ProductImage(SQLModel, table=True):
    __tablename__ = "product_images"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    img_url: str
    sort_order: int = Field(default=0)
