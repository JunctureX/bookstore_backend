from .base import db, BaseModelMixin

class Review(BaseModelMixin, db.Model):
    __tablename__ = "reviews"
    

    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)