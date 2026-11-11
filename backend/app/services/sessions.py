"""Sessions : un jeton signé (JWT) dans un cookie HttpOnly.

- le cookie n'est pas lisible en JavaScript : une faille XSS ne peut pas le voler ;
- `SameSite=Strict` + jeton CSRF en double soumission : un autre site ne peut pas
  agir au nom de l'utilisateur ;
- la déconnexion inscrit le jeton en base (`revoked_tokens`) : elle vaut pour
  tous les workers et survit à un redémarrage ;
- chaque jeton porte la « version de session » du compte (`sv`) : changer de mot
  de passe l'incrémente et ferme d'un coup toutes les sessions ouvertes.
"""
from __future__ import annotations

from datetime import UTC, datetime

from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies,
)

from ..extensions import db
from ..models import RevokedToken, User


def open_session(user: User, body: dict, status: int = 200):
    """Réponse JSON qui pose le cookie de session et le cookie CSRF."""
    token = create_access_token(
        identity=str(user.id), additional_claims={"sv": user.token_version}
    )
    response = jsonify(body)
    response.status_code = status
    set_access_cookies(response, token)
    return response


def revoke_current() -> None:
    """Inscrit le jeton de la requête en cours parmi les jetons révoqués."""
    payload = get_jwt()
    if not payload:
        return
    expires = datetime.fromtimestamp(payload["exp"], UTC).replace(tzinfo=None)
    db.session.merge(RevokedToken(jti=payload["jti"], expires_at=expires))


def close_session(body: dict, status: int = 200):
    """Réponse JSON qui efface les cookies de session."""
    response = jsonify(body)
    response.status_code = status
    unset_jwt_cookies(response)
    return response


def is_revoked(payload: dict) -> bool:
    """Vrai si le jeton ne doit plus être accepté."""
    if db.session.get(RevokedToken, payload["jti"]) is not None:
        return True
    try:
        user = db.session.get(User, int(payload["sub"]))
    except (KeyError, TypeError, ValueError):
        return True
    # Compte supprimé, ou mot de passe changé depuis l'émission du jeton.
    return user is None or payload.get("sv") != user.token_version
