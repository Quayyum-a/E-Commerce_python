from password_encryption import InvalidPasswordError
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
            print("\n=== Course Management System ===")
            print("Choose Role:")
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
                if self.current_user:
                    if role == "student":
                        self.student_menu()
                    else:
                        self.facilitator_menu()
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
        except (ResourceAlreadyExistsError, InvalidPasswordError) as e:
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
        user = self.storage.login_user(email, password)
        if user and user.role == role:
            print(f"Login successful! Welcome, {user.full_name}")
            self.current_user = user
        else:
            print("Invalid email, password, or role")

    def student_menu(self):
        while True:
            print("\nStudent Menu:")
            print("1. Enroll in a course")
            print("2. View enrolled courses")
            print("3. View grades")
            print("4. Logout")
            choice = input("Enter choice (1-4): ").strip()
            if choice == "1":
                self.enroll_course()
            elif choice == "2":
                self.view_enrolled_courses()
            elif choice == "3":
                self.view_grades()
            elif choice == "4":
                self.current_user = None
                print("Logged out")
                break
            else:
                print("Invalid choice")

    def facilitator_menu(self):
        while True:
            print("\nFacilitator Menu:")
            print("1. Create a course")
            print("2. Assign grade")
            print("3. View enrolled students")
            print("4. Logout")
            choice = input("Enter choice (1-4): ").strip()
            if choice == "1":
                self.create_course()
            elif choice == "2":
                self.assign_grade()
            elif choice == "3":
                self.view_enrolled_students()
            elif choice == "4":
                self.current_user = None
                print("Logged out")
                break
            else:
                print("Invalid choice")

    def enroll_course(self):
        try:
            print("\nAvailable Courses:")
            courses = self.storage.get_all_courses()
            if not courses:
                print("No courses available")
                return
            for course in courses:
                print(f"ID: {course.course_id}, Name: {course.name}, Facilitator: {course.facilitator_email}")
            course_id = input("Enter course ID to enroll: ").strip()
            course_id = self._validate_course_id(course_id)
            self.current_user.enroll_in_course(course_id, self.storage)
            print("Enrollment successful!")
        except (InvalidFormatError, ResourceNotFoundError) as e:
            print(f"Error: {e}")

    def view_enrolled_courses(self):
        try:
            courses = self.current_user.view_enrolled_courses(self.storage)
            if not courses:
                print("No enrolled courses")
                return
            print("\nEnrolled Courses:")
            for course in courses:
                print(f"ID: {course.course_id}, Name: {course.name}, Facilitator: {course.facilitator_email}")
        except Exception as e:
            print(f"Error: {e}")

    def view_grades(self):
        try:
            enrollments = self.current_user.view_grades(self.storage)
            if not enrollments:
                print("No grades available")
                return
            print("\nGrades:")
            for enrollment in enrollments:
                course = self.storage.find_course_by_id(enrollment.course_id)
                grade = enrollment.grade if enrollment.grade else "Not graded"
                print(f"Course ID: {enrollment.course_id}, Course Name: {course.name if course else 'Unknown'}, Grade: {grade}")
        except Exception as e:
            print(f"Error: {e}")

    def create_course(self):
        try:
            course_id = input("Enter course ID: ").strip()
            course_id = self._validate_course_id(course_id)
            name = input("Enter course name: ").strip()
            name = self._validate_course_name(name)
            self.current_user.create_course(course_id, name, self.storage)
            print("Course created successfully!")
        except (InvalidFormatError, EmptyFieldError) as e:
            print(f"Error: {e}")

    def assign_grade(self):
        try:
            course_id = input("Enter course ID: ").strip()
            course_id = self._validate_course_id(course_id)
            student_email = input("Enter student email: ").strip()
            student_email = self._validate_email(student_email)
            grade = input("Enter grade (e.g., A, B, C): ").strip().upper()
            grade = self._validate_grade(grade)
            self.current_user.assign_grade(course_id, student_email, grade, self.storage)
            print("Grade assigned successfully!")
        except (InvalidFormatError, ResourceNotFoundError, InvalidEmailError) as e:
            print(f"Error: {e}")

    def view_enrolled_students(self):
        try:
            course_id = input("Enter course ID: ").strip()
            course_id = self._validate_course_id(course_id)
            enrollments = self.current_user.view_enrolled_students(course_id, self.storage)
            if not enrollments:
                print("No students enrolled in this course")
                return
            print("\nEnrolled Students:")
            for enrollment in enrollments:
                print(f"Student Email: {enrollment.student_email}, Grade: {enrollment.grade or 'Not graded'}")
        except (InvalidFormatError, ResourceNotFoundError) as e:
            print(f"Error: {e}")