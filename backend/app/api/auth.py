"""Inscription, connexion, deconnexion, profil."""
import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import or_

from ..extensions import db
from ..models import User
from ..services import activity

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Jetons revoques (deconnexion). En production : Redis plutot que la memoire.
REVOKED: set[str] = set()


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    errors = {}
    if not EMAIL_RE.match(email):
        errors["email"] = "Email invalide."
    if len(username) < 3:
        errors["username"] = "3 caracteres minimum."
    if len(password) < 8:
        errors["password"] = "8 caracteres minimum."
    if errors:
        return jsonify({"errors": errors}), 400

    exists = User.query.filter(
        or_(User.email == email, User.username == username)
    ).first()
    if exists:
        return jsonify({"errors": {"email": "Compte deja existant."}}), 409

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    activity.log("register", user.id)
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("email") or data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter(
        or_(User.email == identifier, User.username == identifier)
    ).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Identifiants incorrects."}), 401

    activity.log("login", user.id)
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()})


@bp.post("/logout")
@jwt_required()
def logout():
    REVOKED.add(get_jwt()["jti"])
    activity.log("logout", int(get_jwt_identity()))
    return jsonify({"message": "Deconnecte."})


@bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        return jsonify({"error": "Utilisateur introuvable."}), 404
    return jsonify({"user": user.to_dict()})
