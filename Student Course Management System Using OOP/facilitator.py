from course import Course
from user import User
from exception import InvalidFormatError, ResourceNotFoundError

class Facilitator(User):
    def __init__(self, full_name, email, password, is_encrypted=False):
        super().__init__(full_name, email, password, role='facilitator', is_encrypted=is_encrypted)
        self.created_courses = []

    def create_course(self, course_id, name, storage):

        course = Course(course_id, name, self.email)
        storage.save_course(course)
        self.created_courses.append(course_id)
        return True

    def assign_grade(self, course_id, student_email, grade, storage):
        course = storage.find_course_by_id(course_id)
        if not course:
            raise ResourceNotFoundError("Course not found")
        enrollment = storage.find_enrollment_by_course_and_student(course_id, student_email)
        if not enrollment:
            raise ResourceNotFoundError("Student not enrolled in this course")

        enrollment.grade = grade
        storage.save_enrollment(enrollment)
        return True

    def view_enrolled_students(self, course_id, storage):
        if not course_id or not course_id.isalnum():
            raise InvalidFormatError("Course ID must be non-empty and alphanumeric")
        course = storage.find_course_by_id(course_id)
        if not course:
            raise ResourceNotFoundError("Course not found")
        return storage.find_enrollments_by_course(course_id)