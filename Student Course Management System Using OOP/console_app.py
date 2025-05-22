from student import Student
from facilitator import Facilitator
from storage import Storage
from exception import InvalidFormatError, EmptyFieldError, ResourceNotFoundError, ResourceAlreadyExistsError, InvalidEmailError

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
            role_choice = input("Enter choice (1-3): ")
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
            action_choice = input("Enter choice (1-3): ")
            if action_choice == "1":
                self.login(role)
            elif action_choice == "2":
                self.register(role)
            elif action_choice == "3":
                continue

    def register(self, role):
        full_name = input("Full Name: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        try:
            user = Student(full_name, email, password) if role == "student" else Facilitator(full_name, email, password)
            self.storage.save_user(user)
            print("Registration successful!")
        except (InvalidEmailError, EmptyFieldError, ResourceAlreadyExistsError) as e:
            print(f"Error: {e}")

    def login(self, role):
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        try:
            user = self.storage.login_user(email, password)
            if user and user.role == role:
                self.current_user = user
                print(f"Welcome, {user.full_name}!")
                self.show_menu()
            else:
                print("Invalid credentials or role mismatch")
        except (EmptyFieldError, InvalidEmailError) as e:
            print(f"Error: {e}")

    def show_menu(self):
        while True:
            if isinstance(self.current_user, Student):
                print("\nStudent Menu:")
                print("1. View Enrolled Courses")
                print("2. View Grades")
                print("3. Enroll in Course")
                print("4. Logout")
                choice = input("Enter choice: ")
                if choice == "1":
                    self.view_enrolled_courses()
                elif choice == "2":
                    self.view_grades()
                elif choice == "3":
                    self.enroll_in_course()
                elif choice == "4":
                    self.current_user = None
                    break
            elif isinstance(self.current_user, Facilitator):
                print("\nFacilitator Menu:")
                print("1. Create Course")
                print("2. Assign Grade")
                print("3. View Enrolled Students")
                print("4. Logout")
                choice = input("Enter choice: ")
                if choice == "1":
                    self.create_course()
                elif choice == "2":
                    self.assign_grade()
                elif choice == "3":
                    self.view_enrolled_students()
                elif choice == "4":
                    self.current_user = None
                    break

    def view_enrolled_courses(self):
        try:
            courses = self.current_user.view_enrolled_courses(self.storage)
            if courses:
                for course in courses:
                    print(f"Course ID: {course.course_id}, Name: {course.name}, Facilitator: {course.facilitator_email}")
            else:
                print("No enrolled courses")
        except Exception as e:
            print(f"Error: {e}")

    def view_grades(self):
        try:
            enrollments = self.current_user.view_grades(self.storage)
            if enrollments:
                for enrollment in enrollments:
                    grade = enrollment.grade if enrollment.grade else "Not graded"
                    print(f"Course ID: {enrollment.course_id}, Grade: {grade}")
            else:
                print("No grades available")
        except Exception as e:
            print(f"Error: {e}")

    def enroll_in_course(self):
        course_id = input("Enter Course ID: ").strip()
        try:
            self.current_user.enroll_in_course(course_id, self.storage)
            print("Enrollment successful!")
        except (InvalidFormatError, ResourceNotFoundError) as e:
            print(f"Error: {e}")

    def create_course(self):
        course_id = input("Enter Course ID: ").strip()
        name = input("Enter Course Name: ").strip()
        try:
            self.current_user.create_course(course_id, name, self.storage)
            print("Course created successfully!")
        except (InvalidFormatError, EmptyFieldError) as e:
            print(f"Error: {e}")

    def assign_grade(self):
        course_id = input("Enter Course ID: ").strip()
        student_email = input("Enter Student Email: ").strip()
        grade = input("Enter Grade: ").strip()
        try:
            self.current_user.assign_grade(course_id, student_email, grade, self.storage)
            print("Grade assigned successfully!")
        except (InvalidFormatError, InvalidEmailError, ResourceNotFoundError) as e:
            print(f"Error: {e}")

    def view_enrolled_students(self):
        course_id = input("Enter Course ID: ").strip()
        try:
            students = self.current_user.view_enrolled_students(course_id, self.storage)
            if students:
                for student in students:
                    print(f"Student Email: {student.student_email}, Grade: {student.grade or 'Not graded'}")
            else:
                print("No students enrolled")
        except (InvalidFormatError, ResourceNotFoundError) as e:
            print(f"Error: {e}")