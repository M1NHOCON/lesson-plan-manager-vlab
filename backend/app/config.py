import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", "5000"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lesson_plans.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER")
