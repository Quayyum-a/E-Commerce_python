import re
from exception import InvalidEmailError, EmptyFieldError

class User:
    def __init__(self, full_name, email, password, role):
        if not full_name.strip():
            raise EmptyFieldError("Full name cannot be empty")
        if not self._is_valid_email(email):
            raise InvalidEmailError("Invalid email format")
        if not password.strip():
            raise EmptyFieldError("Password cannot be empty")
        self.full_name = full_name
        self.email = email
        self.password = password
        self.role = role

    @staticmethod
    def _is_valid_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))