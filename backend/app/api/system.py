"""Endpoints techniques : sante (pour Docker / CI/CD) et assistant IA libre."""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import text

from ..extensions import db
from ..services.ai import AIUnavailable, ask, provider

bp = Blueprint("system", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    checks = {"api": "ok"}
    status = 200
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"erreur: {exc}"
        status = 503
    checks["ai_provider"] = provider() or "offline"
    return jsonify(checks), status


@bp.post("/ai/ask")
@jwt_required()
def ai_ask():
    question = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Question vide."}), 400
    if len(question) > 2000:
        return jsonify({"error": "Question trop longue (2000 caracteres max)."}), 400
    try:
        return jsonify(ask(question))
    except AIUnavailable as exc:
        current_app.logger.warning("IA indisponible : %s", exc)
        return jsonify({"provider": "offline", "answer": str(exc)}), 200
