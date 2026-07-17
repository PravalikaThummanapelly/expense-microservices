import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/expenses_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-this-in-production")
    # This is the address of users-service. Locally it's localhost:5001.
    # Later in Docker/Kubernetes, this becomes a service name instead of
    # "localhost" — that's one of the key things those tools handle for us.
    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:5001")
