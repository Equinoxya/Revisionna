"""Petits outils partagés par les vues."""
from __future__ import annotations

from flask import jsonify, request

from ..services import throttle


def body() -> dict:
    """Corps JSON de la requête (dictionnaire vide s'il est absent ou invalide)."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def text(data: dict, key: str, limit: int = 300) -> str:
    """Champ texte nettoyé ; une valeur d'un autre type est ignorée."""
    value = data.get(key)
    return value.strip()[:limit] if isinstance(value, str) else ""


def secret(data: dict, key: str) -> str:
    """Mot de passe : jamais modifié (ni espaces retirés, ni tronqué ici)."""
    value = data.get(key)
    return value if isinstance(value, str) else ""


def client_ip() -> str:
    """Adresse du client. Fiable derrière un proxy si TRUSTED_PROXIES est réglé."""
    return request.remote_addr or "inconnue"


def too_many(wait: int):
    """Réponse 429 avec le délai à respecter."""
    response = jsonify({
        "error": f"Trop de tentatives. Réessayez dans {throttle.human(wait)}.",
        "retry_after": wait,
    })
    response.status_code = 429
    response.headers["Retry-After"] = str(wait)
    return response
