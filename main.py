from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from app.db import create_db_and_tables
from app.routers import (products, cart, orders, users,
                         admin_orders, admin_products, admin_users,
                         admin_auth, user_auth, wishlist, reviews,
                         admin_promo, promo)
from app.admin_config import ADMIN_URL_SLUG


async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(wishlist.router)
app.include_router(reviews.router)
app.include_router(promo.router)
app.include_router(admin_orders.router)
app.include_router(admin_products.router)
app.include_router(admin_users.router)
app.include_router(admin_auth.router)
app.include_router(user_auth.router)
app.include_router(admin_promo.router)

app.mount("/static", StaticFiles(directory="../frontend2"), name="static")


@app.get("/")
def serve_customer():
    return FileResponse("../frontend2/customer-pages/index.html")


@app.get(f"/{ADMIN_URL_SLUG}")
def serve_admin():
    return RedirectResponse(url="/static/admin-pages/index.html")
