"""Inscription, connexion, déconnexion, changement de mot de passe."""
from __future__ import annotations

import hmac
import re
from datetime import timedelta

from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import current_user, jwt_required, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from ..extensions import db
from ..models import User, username_key, utcnow
from ..services import activity, passwords, sessions, throttle
from .common import body, client_ip, secret, text, too_many

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_MIN, USERNAME_MAX = 3, 30
USERNAME_EXTRA = "._-"

QUARTER = timedelta(minutes=15)
HOUR = timedelta(hours=1)
LOGIN_FAILURES_PER_IP = 50          # par quart d'heure : tolère une salle de classe
REGISTRATIONS_PER_IP = 40           # par heure : idem
PASSWORD_CHECKS_PER_USER = 5        # par quart d'heure


def email_error(email: str) -> str | None:
    if len(email) > 254 or not EMAIL_RE.match(email):
        return "Adresse email invalide."
    return None


def username_error(username: str) -> str | None:
    if not USERNAME_MIN <= len(username) <= USERNAME_MAX:
        return f"Entre {USERNAME_MIN} et {USERNAME_MAX} caractères."
    if not all(char.isalnum() or char in USERNAME_EXTRA for char in username):
        return "Lettres, chiffres, point, tiret et tiret bas uniquement."
    if not username[0].isalnum():
        return "Doit commencer par une lettre ou un chiffre."
    return None


def find_user(identifier: str) -> User | None:
    """Cherche par email s'il y a une arobase, sinon par pseudo (sans casse)."""
    if "@" in identifier:
        return User.query.filter_by(email=identifier.lower()).first()
    return User.query.filter_by(username_key=username_key(identifier)).first()


def confirm_password(user: User, password: str):
    """Vérifie le mot de passe actuel avant une action sensible.

    Renvoie None si c'est bon, sinon la réponse d'erreur à retourner.
    """
    limit = {"limit": PASSWORD_CHECKS_PER_USER, "window": QUARTER}
    wait = throttle.wait_time("password-check", user.id, **limit)
    if wait:
        return too_many(wait)
    if not passwords.verify(user.password_hash, password):
        throttle.hit("password-check", user.id, **limit)
        return jsonify({"errors": {"current_password": "Mot de passe incorrect."}}), 403
    return None


@bp.post("/register")
def register():
    wait = throttle.hit("register-ip", client_ip(), limit=REGISTRATIONS_PER_IP, window=HOUR)
    if wait:
        return too_many(wait)

    data = body()
    email = text(data, "email").lower()
    username = text(data, "username")
    password = secret(data, "password")

    errors = {}
    if problem := email_error(email):
        errors["email"] = problem
    if problem := username_error(username):
        errors["username"] = problem
    if issues := passwords.problems(password, email=email, username=username):
        errors["password"] = " ".join(issues)
    if data.get("accept_terms") is not True:
        errors["accept_terms"] = "Vous devez accepter les conditions d'utilisation."

    expected_code = current_app.config["INVITE_CODE"]
    if expected_code and not hmac.compare_digest(
        text(data, "invite_code").encode(), expected_code.encode()
    ):
        errors["invite_code"] = "Code d'invitation incorrect."
    if errors:
        return jsonify({"errors": errors}), 400

    conflicts = {}
    if User.query.filter_by(email=email).first():
        conflicts["email"] = "Un compte existe déjà avec cette adresse."
    if User.query.filter_by(username_key=username_key(username)).first():
        conflicts["username"] = "Ce nom d'utilisateur est déjà pris."
    if conflicts:
        return jsonify({"errors": conflicts}), 409

    now = utcnow()
    user = User(
        email=email,
        username=username,
        username_key=username_key(username),
        password_hash=passwords.hash_password(password),
        terms_accepted_at=now,
        terms_version=current_app.config["TERMS_VERSION"],
        last_login_at=now,
    )
    db.session.add(user)
    db.session.commit()

    activity.log("register", user.id)
    return sessions.open_session(user, {"user": user.to_dict()}, status=201)


@bp.post("/login")
def login():
    data = body()
    identifier = (
        text(data, "identifier") or text(data, "email") or text(data, "username")
    ).casefold()
    password = secret(data, "password")
    ip = client_ip()

    # Les blocages sont vérifiés AVANT le mot de passe : pendant une attente, la
    # réponse est la même que le mot de passe soit juste ou faux.
    wait = throttle.wait_time(
        "login-ip", ip, limit=LOGIN_FAILURES_PER_IP, window=QUARTER
    ) or throttle.login_wait(identifier)
    if wait:
        return too_many(wait)

    user = find_user(identifier) if identifier else None
    if not passwords.verify(user.password_hash if user else None, password):
        throttle.login_failed(identifier)
        throttle.hit("login-ip", ip, limit=LOGIN_FAILURES_PER_IP, window=QUARTER)
        current_app.logger.info("connexion refusée")
        # Même message que le compte existe ou non.
        return jsonify({"error": "Identifiants incorrects."}), 401

    throttle.login_succeeded(identifier)
    user.last_login_at = utcnow()
    db.session.commit()

    activity.log("login", user.id)
    return sessions.open_session(user, {"user": user.to_dict()})


@bp.post("/logout")
def logout():
    """Ferme la session. Répond toujours 200 et efface toujours les cookies."""
    try:
        verify_jwt_in_request()
    except (JWTExtendedException, PyJWTError):
        pass  # jeton absent, expiré ou déjà révoqué : rien à révoquer
    else:
        sessions.revoke_current()
        db.session.commit()
        activity.log("logout", current_user.id)
    return sessions.close_session({"message": "Déconnecté."})


@bp.get("/me")
@jwt_required()
def me():
    return jsonify({"user": current_user.to_dict()})


@bp.post("/password")
@jwt_required()
def change_password():
    data = body()
    refused = confirm_password(current_user, secret(data, "current_password"))
    if refused:
        return refused

    new_password = secret(data, "new_password")
    issues = passwords.problems(
        new_password, email=current_user.email, username=current_user.username
    )
    if passwords.verify(current_user.password_hash, new_password):
        issues = ["Le nouveau mot de passe doit être différent de l'actuel."]
    if issues:
        return jsonify({"errors": {"new_password": " ".join(issues)}}), 400

    current_user.password_hash = passwords.hash_password(new_password)
    current_user.token_version += 1     # ferme toutes les sessions ouvertes…
    sessions.revoke_current()
    db.session.commit()

    activity.log("password_changed", current_user.id)
    # … et en rouvre une pour cet appareil.
    return sessions.open_session(current_user, {"message": "Mot de passe modifié."})
