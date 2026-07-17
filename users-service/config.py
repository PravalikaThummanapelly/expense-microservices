import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Format: mysql+pymysql://<user>:<password>@<host>:<port>/<database>
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/users_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-this-in-production")
