import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:5001")
    EXPENSES_SERVICE_URL = os.getenv("EXPENSES_SERVICE_URL", "http://localhost:5002")
