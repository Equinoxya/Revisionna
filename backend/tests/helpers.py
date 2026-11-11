"""Outils communs aux tests : ouverture de session par cookie, en-tête CSRF."""
from app.config import TestConfig

PASSWORD = "cahier-de-texte-42"
CSRF_COOKIE = TestConfig.JWT_ACCESS_CSRF_COOKIE_NAME
SESSION_COOKIE = TestConfig.JWT_ACCESS_COOKIE_NAME
SESSION_PATH = TestConfig.JWT_ACCESS_COOKIE_PATH


def csrf(client) -> dict:
    """En-tête CSRF correspondant à la session ouverte dans ce client."""
    cookie = client.get_cookie(CSRF_COOKIE)
    return {"X-CSRF-Token": cookie.value} if cookie else {}


def register(client, username="eleve", email=None, password=PASSWORD, **extra):
    return client.post("/api/auth/register", json={
        "email": email or f"{username.lower()}@test.fr",
        "username": username,
        "password": password,
        "accept_terms": True,
        **extra,
    })


def login(client, identifier="eleve@test.fr", password=PASSWORD):
    return client.post("/api/auth/login", json={"identifier": identifier, "password": password})
