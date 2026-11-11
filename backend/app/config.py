"""Configuration de l'application : tout vient de l'environnement (12 facteurs)."""
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

TRUE = {"1", "true", "yes", "on", "oui"}


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    return default if raw is None or raw == "" else raw.strip().lower() in TRUE


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "") or default)
    except ValueError:
        return default


# Sans indication, on se considère en production : c'est le réglage sûr.
ENVIRONMENT = (os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "production").lower()
PRODUCTION = ENVIRONMENT not in ("development", "testing")

# Clé de confort pour le développement local uniquement.
DEV_SECRET = "cle-de-developpement-a-ne-jamais-utiliser-en-production"
PLACEHOLDERS = ("change-me", "changeme", "dev-secret", "secret", DEV_SECRET)
MIN_SECRET_LENGTH = 32


class Config:
    ENVIRONMENT = ENVIRONMENT
    PRODUCTION = PRODUCTION

    SECRET_KEY = os.getenv("SECRET_KEY") or ("" if PRODUCTION else DEV_SECRET)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ("" if PRODUCTION else DEV_SECRET + "-jwt")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///revisionna.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Aucune requête légitime n'approche cette taille (code d'un TP : 20 000 caractères).
    MAX_CONTENT_LENGTH = 256 * 1024

    # --- Session : jeton signé dans un cookie HttpOnly, jamais lisible en JavaScript.
    # Le jeton CSRF (cookie lisible) doit être renvoyé en en-tête à chaque écriture.
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=_int("SESSION_HOURS", 12))
    JWT_SESSION_COOKIE = True            # disparaît à la fermeture du navigateur
    JWT_COOKIE_SECURE = _flag("COOKIE_SECURE", PRODUCTION)
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_COOKIE_NAME = "revisionna_session"
    JWT_ACCESS_COOKIE_PATH = "/api/"
    JWT_ACCESS_CSRF_COOKIE_NAME = "revisionna_csrf"
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-Token"

    # Nombre de reverse proxies de confiance devant l'API (nginx = 1).
    # Sert à retrouver la vraie adresse du client pour limiter les tentatives.
    TRUSTED_PROXIES = _int("TRUSTED_PROXIES", 0)

    # --- Inscription et données personnelles
    INVITE_CODE = os.getenv("INVITE_CODE", "")       # vide = inscriptions ouvertes
    TERMS_VERSION = "2026-11-11"                     # à changer quand les CGU changent
    INACTIVE_ACCOUNT_MONTHS = _int("INACTIVE_ACCOUNT_MONTHS", 24)
    ACTIVITY_RETENTION_DAYS = _int("ACTIVITY_RETENTION_DAYS", 180)

    # --- Journal d'activité (MongoDB, optionnel)
    MONGO_URL = os.getenv("MONGO_URL", "")
    MONGO_DB = os.getenv("MONGO_DB", "revisionna")

    # --- Tuteur IA : "ollama" (local), "openai" (distant) ou vide (désactivé)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Correction des TP : service isolé (production) ou sous-processus local (dev)
    RUNNER_TIMEOUT = _int("RUNNER_TIMEOUT", 8)
    RUNNER_SOCKET = os.getenv("RUNNER_SOCKET", "")
    ALLOW_LOCAL_RUNNER = _flag("ALLOW_LOCAL_RUNNER", not PRODUCTION)


class TestConfig(Config):
    TESTING = True
    ENVIRONMENT = "testing"
    PRODUCTION = False
    SECRET_KEY = "cle-de-test-uniquement-0123456789abcdef"
    JWT_SECRET_KEY = "cle-jwt-de-test-uniquement-0123456789abcdef"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    JWT_COOKIE_SECURE = False
    TRUSTED_PROXIES = 0
    INVITE_CODE = ""
    AI_PROVIDER = ""
    MONGO_URL = ""
    RUNNER_SOCKET = ""
    ALLOW_LOCAL_RUNNER = True


def settings_problems(config) -> list[str]:
    """Réglages qui rendraient une mise en production dangereuse."""
    problems = []
    for name in ("SECRET_KEY", "JWT_SECRET_KEY"):
        value = config.get(name) or ""
        if len(value) < MIN_SECRET_LENGTH:
            problems.append(f"{name} doit faire au moins {MIN_SECRET_LENGTH} caractères")
        elif any(marker in value.lower() for marker in PLACEHOLDERS):
            problems.append(f"{name} contient une valeur d'exemple")
    if config.get("SECRET_KEY") and config.get("SECRET_KEY") == config.get("JWT_SECRET_KEY"):
        problems.append("SECRET_KEY et JWT_SECRET_KEY doivent être différentes")
    return problems
