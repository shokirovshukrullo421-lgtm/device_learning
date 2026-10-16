from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from .database import SessionLocal
from .models import User
from .security import hash_password
from .routers import auth, products, cart, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Admin avtomatik yaratiladi
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username == "admin")):
            db.add(User(username="admin", password_hash=hash_password("admin123"), role="admin"))
            db.commit()
    yield


app = FastAPI(title="Do'kon", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(admin.router)

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")