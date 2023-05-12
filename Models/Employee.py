import hashlib
import os


class Employee:
    def __init__(
        self, number: int, name: str, password: str = "", encryptedPassword: str = ""
    ) -> None:
        self.number = number
        self.name = name.strip()
        self.encryptedPassword = encryptedPassword
        if password != "":
            self.encryptedPassword = self._encrypt_password(password)

    def equals_password(self, password: str):
        if self.encryptedPassword == "":
            return True
        return self.encryptedPassword == self._encrypt_password(password)

    def _encrypt_password(self, password: str):
        password = os.environ.get("HALT") + password.strip()
        return hashlib.md5(password.encode()).hexdigest()
