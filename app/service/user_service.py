# book_store_backend/app/service/user_service.py
from app.models import User, db
from werkzeug.security import generate_password_hash

def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def create_user(data):
    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        user_type=data.get('user_type', 'customer')
    )
    new_user.set_password(data.get('password'))
    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_user(user_id, data):
    user = User.query.get(user_id)
    if user:
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.user_type = data.get('user_type', user.user_type)
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return user
    return None

def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False