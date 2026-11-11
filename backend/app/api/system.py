"""Points d'entrée techniques : santé, informations publiques, question libre à l'IA."""
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import text

from sandbox import client

from ..extensions import db
from ..services import passwords
from ..services.ai import AIUnavailable, ask, provider
from .common import body, too_many
from .workspace import ai_quota

bp = Blueprint("system", __name__, url_prefix="/api")


def _runner_status() -> str:
    socket_path = current_app.config.get("RUNNER_SOCKET")
    if socket_path:
        try:
            isolated = client.health(socket_path).get("isolated")
        except client.RunnerUnavailable:
            return "indisponible"
        return "isolé" if isolated else "socket sans comptes jetables"
    return "local" if current_app.config.get("ALLOW_LOCAL_RUNNER") else "désactivé"


@bp.get("/health")
def health():
    """Sonde pour Docker et la CI : l'API répond-elle, la base aussi ?"""
    checks = {"api": "ok", "runner": _runner_status()}
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:  # noqa: BLE001
        current_app.logger.exception("base de données injoignable")
        checks["database"] = "erreur"
        return jsonify(checks), 503
    return jsonify(checks)


@bp.get("/meta")
def meta():
    """Ce que l'interface doit savoir avant toute connexion (rien de sensible)."""
    name = provider() or "offline"
    return jsonify({
        "ai_provider": name,
        "ai_external": name == "openai",   # vrai = des données quittent le serveur
        "invite_required": bool(current_app.config["INVITE_CODE"]),
        "terms_version": current_app.config["TERMS_VERSION"],
        "password_min_length": passwords.MIN_LENGTH,
        "session_hours": int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds() // 3600),
        "inactive_account_months": current_app.config["INACTIVE_ACCOUNT_MONTHS"],
        "activity_retention_days": current_app.config["ACTIVITY_RETENTION_DAYS"],
    })


@bp.post("/ai/ask")
@jwt_required()
def ai_ask():
    question = body().get("question")
    question = question.strip() if isinstance(question, str) else ""
    if not question:
        return jsonify({"error": "Question vide."}), 400
    if len(question) > 2000:
        return jsonify({"error": "Question trop longue (2 000 caractères au maximum)."}), 400

    wait = ai_quota()
    if wait:
        return too_many(wait)
    try:
        return jsonify(ask(question))
    except AIUnavailable as exc:
        current_app.logger.warning("IA indisponible : %s", exc)
        return jsonify({"provider": "secours", "answer": "Le tuteur est indisponible pour le moment."})
