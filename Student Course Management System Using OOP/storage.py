from user import User
from student import Student
from facilitator import Facilitator
from course import Course
from enrollment import Enrollment
from exception import ResourceAlreadyExistsError, EmptyFieldError, InvalidEmailError, InvalidFormatError
from password_encryption import PasswordEncryption, InvalidPasswordError

class Storage:
    def __init__(self, users_file="users.txt", courses_file="courses.txt", enrollments_file="enrollments.txt"):
        self.users_file = users_file
        self.courses_file = courses_file
        self.enrollments_file = enrollments_file

    def save_user(self, user):
        existing_user = self.find_user_by_email(user.email)
        if existing_user:
            raise ResourceAlreadyExistsError("Email already registered")
        with open(self.users_file, 'a') as file:
            file.write(f"{user.full_name.replace(',', ' ')},{user.email},{user.password},{user.role}\n")

    def find_user_by_email(self, email):
        if not User._is_valid_email(email):
            raise InvalidEmailError("Invalid email format")
        try:
            with open(self.users_file, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 4 and parts[1] == email:
                        role = parts[3]
                        if role == "student":
                            return Student(parts[0], parts[1], parts[2], is_encrypted=True)
                        elif role == "facilitator":
                            return Facilitator(parts[0], parts[1], parts[2], is_encrypted=True)
                return None
        except FileNotFoundError:
            return None

    def login_user(self, email, password):
        if not email or not password:
            raise EmptyFieldError("Email and password cannot be empty")
        try:
            encrypted_password = PasswordEncryption(password).encrypt()
            user = self.find_user_by_email(email)
            if user and user.password == encrypted_password:
                return user
            return None
        except InvalidPasswordError as e:
            print(f"Error: {e}")
            return None

    def save_course(self, course):
        with open(self.courses_file, 'a') as file:
            file.write(f"{course.course_id},{course.name},{course.facilitator_email}\n")

    def find_course_by_id(self, course_id):
        try:
            with open(self.courses_file, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 3 and parts[0] == course_id:
                        return Course(parts[0], parts[1], parts[2])
                return None
        except FileNotFoundError:
            return None

    def get_all_courses(self):
        try:
            with open(self.courses_file, 'r') as file:
                courses = []
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        courses.append(Course(parts[0], parts[1], parts[2]))
                return courses
        except FileNotFoundError:
            return []

    def save_enrollment(self, enrollment):
        enrollments = self.find_all_enrollments()
        updated = False
        for e in enrollments:
            if e.course_id == enrollment.course_id and e.student_email == enrollment.student_email:
                e.grade = enrollment.grade
                updated = True
                break
        if not updated:
            enrollments.append(enrollment)
        with open(self.enrollments_file, 'w') as file:
            for e in enrollments:
                file.write(f"{e.course_id},{e.student_email},{e.grade or ''}\n")

    def find_enrollments_by_student(self, student_email):
        if not Enrollment._is_valid_email(student_email):
            raise InvalidEmailError("Invalid student email format")
        try:
            with open(self.enrollments_file, 'r') as file:
                enrollments = []
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 2 and parts[1] == student_email:
                        enrollments.append(Enrollment(parts[0], parts[1], parts[2] if len(parts) > 2 and parts[2] else None))
                return enrollments
        except FileNotFoundError:
            return []

    def find_enrollments_by_course(self, course_id):
        if not course_id or not course_id.isalnum():
            raise InvalidFormatError("Course ID must be non-empty and alphanumeric")
        try:
            with open(self.enrollments_file, 'r') as file:
                enrollments = []
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 2 and parts[0] == course_id:
                        enrollments.append(Enrollment(parts[0], parts[1], parts[2] if len(parts) > 2 and parts[2] else None))
                return enrollments
        except FileNotFoundError:
            return []

    def find_enrollment_by_course_and_student(self, course_id, student_email):
        enrollments = self.find_enrollments_by_student(student_email)
        for enrollment in enrollments:
            if enrollment.course_id == course_id:
                return enrollment
        return None

    def find_all_enrollments(self):
        try:
            with open(self.enrollments_file, 'r') as file:
                enrollments = []
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        enrollments.append(Enrollment(parts[0], parts[1], parts[2] if len(parts) > 2 and parts[2] else None))
                return enrollments
        except FileNotFoundError:
            return []