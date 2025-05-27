from .base import db, BaseModelMixin
from sqlalchemy import DECIMAL, CheckConstraint

class OrderItem(BaseModelMixin, db.Model):
    __tablename__ = "order_items"
    
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(DECIMAL(10, 2), nullable=False)
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name = "ck_quantity_positive"),
    )