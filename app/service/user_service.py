# book_store_backend/app/service/user_service.py
from app.models import User, Book, Order, db
from werkzeug.security import generate_password_hash
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

def book_recommendation(user_id):
    # 获取用户的历史购买书籍
    user = get_user_by_id(user_id)
    if not user:
        return []
    orders = Order.query.filter_by(user_id=user_id).all()
    purchased_book_ids = []
    for order in orders:
        for item in order.items:
            purchased_book_ids.append(item.book_id)

    # 基于内容的推荐
    all_books = Book.query.all()
    if purchased_book_ids:
        purchased_books = Book.query.filter(Book.id.in_(purchased_book_ids)).all()
        purchased_titles = [book.title for book in purchased_books]
        all_titles = [book.title for book in all_books]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_titles)
        purchased_tfidf = vectorizer.transform(purchased_titles)

        content_similarities = cosine_similarity(purchased_tfidf, tfidf_matrix)
        content_scores = content_similarities.sum(axis=0)
    else:
        content_scores = np.zeros(len(all_books))

    # 基于协同过滤的推荐
    user_book_matrix = {}
    all_orders = Order.query.all()
    for order in all_orders:
        user_id = order.user_id
        if user_id not in user_book_matrix:
            user_book_matrix[user_id] = []
        for item in order.items:
            user_book_matrix[user_id].append(item.book_id)

    similar_users = []
    for other_user_id, other_books in user_book_matrix.items():
        if other_user_id != user_id:
            common_books = set(purchased_book_ids).intersection(set(other_books))
            if common_books:
                similar_users.append(other_user_id)

    cf_scores = Counter()
    for similar_user_id in similar_users:
        for book_id in user_book_matrix[similar_user_id]:
            cf_scores[book_id] += 1

    # 合并两种推荐结果
    final_scores = {}
    for i, book in enumerate(all_books):
        final_scores[book.id] = content_scores[i] + cf_scores[book.id]

    # 排除用户已经购买过的书籍
    for book_id in purchased_book_ids:
        final_scores[book_id] = 0

    # 按得分排序并返回前5本
    sorted_books = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
    top_5_books = [book_id for book_id, score in sorted_books[:5]]

    return top_5_books
