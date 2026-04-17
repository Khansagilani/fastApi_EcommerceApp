from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db import create_db_and_tables
from app.routers import products, cart, orders, users, admin_orders, admin_products, admin_users
from app.routers import auth
from app.routers import user_auth


async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Middleware must be added first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then routers
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(admin_orders.router)
app.include_router(admin_products.router)
app.include_router(admin_users.router)
app.include_router(auth.router)
app.include_router(user_auth.router)

# Then static files and frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")
# It doesn't actually care what's inside the file
# "Every file inside the frontend/ folder — whatever it is — I will serve it as-is without touching it"
# mount mean attatch with the url


@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")
