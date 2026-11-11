"""Politique et vérification des mots de passe.

Règle retenue : 12 caractères minimum, avec au moins une lettre et un chiffre.
Alphabet garanti de 36 symboles sur 12 positions, soit environ 62 bits
d'entropie : au-dessus des 50 bits que la CNIL recommande quand l'accès est
par ailleurs ralenti après plusieurs échecs (délibération n° 2022-100), ce que
fait `services/throttle.py`.

Stockage : scrypt avec sel (valeur par défaut de Werkzeug), l'une des fonctions
citées par la CNIL et l'ANSSI.
"""
from __future__ import annotations

from functools import cache

from werkzeug.security import check_password_hash, generate_password_hash

MIN_LENGTH = 12
MAX_LENGTH = 128

# Mots de passe répandus qui passeraient la règle de longueur.
COMMON = frozenset({
    "motdepasse123", "motdepasse1234", "motdepasse2026", "azertyuiop12", "azertyuiop123",
    "azerty123456", "123456azerty", "qwertyuiop12", "qwertyuiop123", "qwerty123456",
    "123456qwerty", "password1234", "password12345", "passw0rd1234", "123456789abc",
    "abc123456789", "abcd12345678", "abcdef123456", "1234567890ab", "1234567890az",
    "1q2w3e4r5t6y", "iloveyou1234", "jetaime12345", "bonjour12345", "soleil123456",
    "chocolat1234", "doudou123456", "loulou123456", "admin1234567", "administrateur1",
    "changeme1234", "welcome12345", "letmein12345", "football1234", "revisionna123",
    "revisionna2026",
})


def problems(password: str, *, email: str = "", username: str = "") -> list[str]:
    """Raisons de refuser ce mot de passe (liste vide s'il est acceptable)."""
    if len(password) < MIN_LENGTH:
        return [f"{MIN_LENGTH} caractères minimum."]
    if len(password) > MAX_LENGTH:
        return [f"{MAX_LENGTH} caractères maximum."]

    issues = []
    if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
        issues.append("Il faut au moins une lettre et un chiffre.")

    lowered = password.casefold()
    if lowered in COMMON or len(set(lowered)) < 5:
        issues.append("Ce mot de passe est trop courant ou trop répétitif.")

    for piece in (username, email.split("@")[0]):
        if len(piece) >= 4 and piece.casefold() in lowered:
            issues.append("Il ne doit pas contenir votre nom d'utilisateur ni votre email.")
            break
    return issues


def hash_password(password: str) -> str:
    return generate_password_hash(password)


@cache
def _decoy() -> str:
    return generate_password_hash("leurre-pour-un-compte-inexistant")


def verify(password_hash: str | None, password: str) -> bool:
    """Vérifie un mot de passe en temps comparable, que le compte existe ou non.

    Sans le leurre, une réponse immédiate trahirait l'absence de compte.
    """
    if len(password) > MAX_LENGTH:
        password = password[:MAX_LENGTH]
        password_hash = None
    if password_hash is None:
        check_password_hash(_decoy(), password)
        return False
    return check_password_hash(password_hash, password)
