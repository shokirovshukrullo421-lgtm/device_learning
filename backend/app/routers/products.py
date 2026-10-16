from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product, User
from ..schemas import ProductIn, ProductOut
from ..security import get_current_user, require_admin

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(Product).order_by(Product.id.desc())).all()


@router.post("", response_model=ProductOut)
def create_product(data: ProductIn, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    p = Product(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Mahsulot topilmadi")
    db.delete(p)
    db.commit()
    return {"ok": True}