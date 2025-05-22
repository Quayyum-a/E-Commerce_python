from student import Student
from facilitator import Facilitator
from storage import Storage
from exception import InvalidFormatError, EmptyFieldError, ResourceNotFoundError, ResourceAlreadyExistsError, InvalidEmailError
from enrollment import Enrollment

class ConsoleApp:
    def __init__(self):
        self.storage = Storage()
        self.current_user = None

    def start(self):
        while True:
            print("\nChoose Role:")
            print("1. Student")
            print("2. Facilitator")
            print("3. Exit")
            role_choice = input("Enter choice (1-3): ").strip()
            if role_choice == "3":
                break
            if role_choice not in ["1", "2"]:
                print("Invalid role choice")
                continue
            role = "student" if role_choice == "1" else "facilitator"
            print(f"\n{role.capitalize()} Menu:")
            print("1. Login")
            print("2. Register")
            print("3. Back")
            action_choice = input("Enter choice (1-3): ").strip()
            if action_choice == "1":
                self.login(role)
            elif action_choice == "2":
                self.register(role)
            elif action_choice == "3":
                continue

    def _validate_full_name(self, full_name):
        if not full_name.strip():
            raise EmptyFieldError("Full name cannot be empty")
        return full_name

    def _validate_email(self, email):
        if not Student._is_valid_email(email):
            raise InvalidEmailError("Invalid email format")
        return email

    def _validate_password(self, password):
        if not password.strip():
            raise EmptyFieldError("Password cannot be empty")
        return password

    def _validate_course_id(self, course_id):
        if not course_id or not course_id.isalnum():
            raise InvalidFormatError("Course ID must be non-empty and alphanumeric")
        return course_id

    def _validate_grade(self, grade):
        if not grade or not Enrollment._is_valid_grade(grade):
            raise InvalidFormatError("Grade must be a valid letter grade (e.g., A, B, C)")
        return grade

    def _validate_course_name(self, name):
        if not name.strip():
            raise EmptyFieldError("Course name cannot be empty")
        return name

    def register(self, role):
        while True:
            try:
                full_name = input("Full Name: ").strip()
                full_name = self._validate_full_name(full_name)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")
        while True:
            try:
                email = input("Email: ").strip()
                email = self._validate_email(email)
                break
            except InvalidEmailError as e:
                print(f"Error: {e}")
        while True:
            try:
                password = input("Password: ").strip()
                password = self._validate_password(password)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")
        try:
            user = Student(full_name, email, password) if role == "student" else Facilitator(full_name, email, password)
            self.storage.save_user(user)
            print("Registration successful!")
        except ResourceAlreadyExistsError as e:
            print(f"Error: {e}")

    def login(self, role):
        while True:
            try:
                email = input("Email: ").strip()
                email = self._validate_email(email)
                break
            except InvalidEmailError as e:
                print(f"Error: {e}")
        while True:
            try:
                password = input("Password: ").strip()
                password = self._validate_password(password)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")
