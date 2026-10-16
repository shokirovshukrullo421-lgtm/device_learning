from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Product, CartItem, Order, OrderItem
from ..schemas import CartAddIn, CartOut, CartItemOut, TopUpIn, OrderOut, OrderItemOut
from ..security import require_user

router = APIRouter(prefix="/api", tags=["cart"])


def build_cart(db: Session, user: User) -> CartOut:
    rows = db.scalars(select(CartItem).where(CartItem.user_id == user.id).order_by(CartItem.id)).all()
    items = [
        CartItemOut(
            product_id=r.product_id,
            name=r.product.name,
            price=float(r.product.price),
            quantity=r.quantity,
            subtotal=float(r.product.price * r.quantity),
        )
        for r in rows
    ]
    return CartOut(items=items, total=sum(i.subtotal for i in items))


@router.get("/cart", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), user: User = Depends(require_user)):
    return build_cart(db, user)


@router.post("/cart", response_model=CartOut)
def add_to_cart(data: CartAddIn, db: Session = Depends(get_db), user: User = Depends(require_user)):
    product = db.get(Product, data.product_id)
    if not product:
        raise HTTPException(404, "Mahsulot topilmadi")
    item = db.scalar(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product.id)
    )
    new_qty = (item.quantity if item else 0) + data.quantity
    if new_qty > product.stock:
        raise HTTPException(400, f"Omborda faqat {product.stock} ta bor")
    if item:
        item.quantity = new_qty
    else:
        db.add(CartItem(user_id=user.id, product_id=product.id, quantity=data.quantity))
    db.commit()
    return build_cart(db, user)


@router.delete("/cart/{product_id}", response_model=CartOut)
def remove_from_cart(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    item = db.scalar(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id)
    )
    if item:
        db.delete(item)
        db.commit()
    return build_cart(db, user)


@router.post("/balance/topup")
def top_up(data: TopUpIn, db: Session = Depends(get_db), user: User = Depends(require_user)):
    u = db.execute(select(User).where(User.id == user.id).with_for_update()).scalar_one()
    u.balance += Decimal(str(data.amount))
    db.commit()
    return {"balance": float(u.balance)}


@router.post("/cart/checkout")
def checkout(db: Session = Depends(get_db), user: User = Depends(require_user)):
    u = db.execute(select(User).where(User.id == user.id).with_for_update()).scalar_one()
    items = db.scalars(select(CartItem).where(CartItem.user_id == u.id)).all()
    if not items:
        raise HTTPException(400, "Savat bo'sh")

    total = Decimal(0)
    products = {}
    for it in items:
        p = db.execute(select(Product).where(Product.id == it.product_id).with_for_update()).scalar_one()
        if p.stock < it.quantity:
            raise HTTPException(400, f"'{p.name}' omborda yetarli emas")
        products[it.id] = p
        total += p.price * it.quantity

    if u.balance < total:
        raise HTTPException(400, "Balans yetarli emas. Avval balansni to'ldiring")

    order = Order(user_id=u.id, total=total)
    db.add(order)
    db.flush()
    for it in items:
        p = products[it.id]
        p.stock -= it.quantity
        db.add(OrderItem(order_id=order.id, product_id=p.id, product_name=p.name,
                         price=p.price, quantity=it.quantity))
        db.delete(it)
    u.balance -= total
    db.commit()
    return {"order_id": order.id, "total": float(total), "balance": float(u.balance)}


@router.get("/orders/my", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), user: User = Depends(require_user)):
    orders = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())).all()
    return [
        OrderOut(id=o.id, username=user.username, total=float(o.total), created_at=o.created_at,
                 items=[OrderItemOut.model_validate(i) for i in o.items])
        for o in orders
    ]