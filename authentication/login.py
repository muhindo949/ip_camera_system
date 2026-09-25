import hashlib

class Authentication:
    def __init__(self):
        """
        static admin account
        """
        self.admin_username = "admin"
        self.admin_password_hash = self.hash_password(
            "angeltonny"
        )

    def hash_password(self, password):
        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()


    def login(self, username, password):
        password_hash = self.hash_password(password)

        if (
            username == self.admin_username
            and password_hash == self.admin_password_hash
        ):
            return True

        return False