import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5435')
    DB_NAME = os.getenv('DB_NAME', 'library_db')
    DB_USER = os.getenv('DB_USER', 'library_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'library_pass')

    # Server
    SERVER_PORT = os.getenv('SERVER_PORT', '50051')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'logs/backend.log')

    # Email/SQS keyword
    ERROR_KEYWORD = os.getenv('ERROR_KEYWORD', '[LIBRARY_ERROR]')
