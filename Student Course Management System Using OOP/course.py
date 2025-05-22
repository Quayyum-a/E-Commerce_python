from exception import InvalidFormatError, EmptyFieldError

class Course:
    def __init__(self, course_id, name, facilitator_email):
        if not course_id or not course_id.isalnum():
            raise InvalidFormatError("Course ID must be non-empty and alphanumeric")
        if not name.strip():
            raise EmptyFieldError("Course name cannot be empty")
        self.course_id = course_id
        self.name = name
        self.facilitator_email = facilitator_email
        self.enrollments = []