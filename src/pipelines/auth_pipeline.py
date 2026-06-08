from src.components.database import DatabaseManager

class AuthPipeline:
    def __init__(self):
        self.db = DatabaseManager()

    def register_user(self, username, password) -> bool:
        # In a production context, passwords should be securely hashed here (e.g., using bcrypt)
        if not username or not password:
            return False
        return self.db.create_user(username, password)

    def login_user(self, username, password) -> bool:
        return self.db.verify_user(username, password)
