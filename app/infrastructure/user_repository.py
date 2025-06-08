from app.domain.user import User
from app import db

class UserRepository:
    def save_user(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def find_user_by_email(self, email):
        return User.query.filter_by(email=email).first()