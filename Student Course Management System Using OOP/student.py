from user import User
from exception import InvalidFormatError, ResourceNotFoundError

class Student(User):
    def __init__(self, full_name, email, password):
        super().__init__(full_name, email, password, role='student')
        self.enrolled_courses = []

    def enroll_in_course(self, course_id, storage):
        if not course_id or not course_id.isalnum():
            raise InvalidFormatError("Course ID must be non-empty and alphanumeric")
        course = storage.find_course_by_id(course_id)
        if not course:
            raise ResourceNotFoundError("Course not found")
        enrollments = storage.find_enrollments_by_student(self.email)
        if any(e.course_id == course_id for e in enrollments):
            return True
        from src.domain.enrollment import Enrollment
        enrollment = Enrollment(course_id, self.email)
        storage.save_enrollment(enrollment)
        self.enrolled_courses.append(course_id)
        return True

    def view_enrolled_courses(self, storage):
        courses = []
        for course_id in self.enrolled_courses:
            course = storage.find_course_by_id(course_id)
            if course:
                courses.append(course)
        return courses

    def view_grades(self, storage):
        return storage.find_enrollments_by_student(self.email)