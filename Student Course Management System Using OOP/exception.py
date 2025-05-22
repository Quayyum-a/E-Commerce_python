class InvalidEmailError(Exception):
    pass

class EmptyFieldError(Exception):
    pass

class ResourceAlreadyExistsError(Exception):
    pass

class InvalidFormatError(Exception):
    pass

class ResourceNotFoundError(Exception):
    pass

class FileOperationError(Exception):
    pass