"""Configuration de l'application (12-factor : tout vient de l'environnement)."""
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///revisionna.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGO_URL = os.getenv("MONGO_URL", "")
    MONGO_DB = os.getenv("MONGO_DB", "revisionna")

    AI_PROVIDER = os.getenv("AI_PROVIDER", "")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Securite du bac a sable d'execution de code
    RUNNER_TIMEOUT = int(os.getenv("RUNNER_TIMEOUT", "8"))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-for-unit-tests-only-32b"
    AI_PROVIDER = ""
    MONGO_URL = ""
