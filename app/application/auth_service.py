from app.domain.user import User
from app.infrastructure.user_repository import UserRepository
from flask_jwt_extended import create_access_token

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, username, email, password, role='customer'):
        if self.user_repo.find_user_by_email(email):
            raise ValueError("Email already exists")
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        return self.user_repo.save_user(user)

    def login_user(self, email, password):
        user = self.user_repo.find_user_by_email(email)
        if user and user.check_password(password):
                return create_access_token(identity={'id': user.id, 'role': user.role})
        raise ValueError("Invalid credentials")