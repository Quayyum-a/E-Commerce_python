import string

class InvalidPasswordError(Exception):
    pass

class PasswordEncryption:
    def __init__(self, password):
        if not isinstance(password, str) or not password:
            raise InvalidPasswordError("Password must be a non-empty string")
        if not all(char in string.printable for char in password):
            raise InvalidPasswordError("Password contains invalid characters")
        self.password = password

    def encrypt(self):
        result = []
        for char in self.password:
            if 'a' <= char.lower() <= 'z':
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base + 13) % 26 + base))
            else:
                result.append(char)
        return ''.join(result)

    def decrypt(self):
        result = []
        for char in self.password:
            if 'a' <= char.lower() <= 'z':
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base - 13) % 26 + base))
            else:
                result.append(char)
        return ''.join(result)