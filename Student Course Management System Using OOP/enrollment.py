import re
from exception import InvalidFormatError, InvalidEmailError

class Enrollment:
    def __init__(self, course_id, student_email, grade=None):
        if not course_id or not course_id.isalnum():
            raise InvalidFormatError("Course ID must be non-empty and alphanumeric")
        if not self._is_valid_email(student_email):
            raise InvalidEmailError("Invalid student email format")
        if grade and not self._is_valid_grade(grade):
            raise InvalidFormatError("Grade must be a valid letter grade (e.g., A, B, C)")
        self.course_id = course_id
        self.student_email = student_email
        self.grade = grade

    @staticmethod
    def _is_valid_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def _is_valid_grade(grade):
        valid_grades = ['A', 'B', 'C', 'D', 'F', 'A+', 'A-', 'B+', 'B-', 'C+', 'C-', 'D+', 'D-']
        return grade in valid_grades