import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "127.0.0.1")
        self.port = os.getenv("DB_PORT", "3306")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "college_assistant_db")
        
        # Initialize database and tables
        self._initialize_db()

    def _get_connection(self, include_db=True):
        """Creates a raw connection to the MySQL server."""
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database if include_db else None
        )

    def _initialize_db(self):
        """Creates the database and schema tables if they do not exist."""
        try:
            # Step 1: Connect without DB to create DB if it doesn't exist
            conn = self._get_connection(include_db=False)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.commit()
            cursor.close()
            conn.close()

            # Step 2: Connect to specific DB to build schema tables
            conn = self._get_connection(include_db=True)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ MySQL Database & Tables verified/initialized successfully.")
        except Error as e:
            print(f"❌ Error during Database Initialization: {e}")

    def create_user(self, username, password):
        """Registers a new user inside the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"❌ Error while registering user: {e}")
            return False

    def verify_user(self, username, password):
        """Verifies if the credentials match a record in the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result and result[0] == password:
                return True
            return False
        except Error as e:
            print(f"❌ Error while validating user: {e}")
            return False
