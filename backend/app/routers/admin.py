from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Order
from ..schemas import UserOut, OrderOut, OrderItemOut
from ..security import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[UserOut])
def users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.get("/orders", response_model=list[OrderOut])
def orders(db: Session = Depends(get_db)):
    rows = db.scalars(select(Order).order_by(Order.id.desc())).all()
    return [
        OrderOut(id=o.id, username=o.user.username, total=float(o.total), created_at=o.created_at,
                 items=[OrderItemOut.model_validate(i) for i in o.items])
        for o in rows
    ]