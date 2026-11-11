"""Fabrique d'application Flask (application factory)."""
import logging

from flask import Flask, jsonify, request
from flask_jwt_extended.exceptions import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config, settings_problems
from .extensions import db, jwt, migrate

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    logging.basicConfig(level=logging.INFO)
    _check_settings(app)

    proxies = app.config["TRUSTED_PROXIES"]
    if proxies:
        # Derrière nginx : la vraie adresse du client et le protocole (https)
        # arrivent dans les en-têtes X-Forwarded-*.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxies, x_proto=proxies, x_host=proxies)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    jwt.init_app(app)

    from .api import account, auth, content, system, workspace

    for module in (auth, account, content, workspace, system):
        app.register_blueprint(module.bp)

    _register_sessions(app)
    _register_guards(app)
    _register_errors(app)

    from . import cli

    cli.register(app)
    return app


def _check_settings(app: Flask) -> None:
    """En production, on refuse de démarrer avec des secrets faibles ou d'exemple."""
    if not app.config["PRODUCTION"]:
        return
    problems = settings_problems(app.config)
    if problems:
        raise RuntimeError(
            "Configuration refusée en production : " + " ; ".join(problems)
            + ". Générez des secrets avec `make env` (voir README)."
        )
    if not app.config["JWT_COOKIE_SECURE"]:
        app.logger.warning(
            "COOKIE_SECURE est désactivé : le cookie de session peut circuler en clair. "
            "À n'accepter que pour un essai local en HTTP."
        )


def _register_sessions(app: Flask) -> None:
    from .models import User
    from .services import sessions

    def refused(message: str):
        # 401 + effacement des cookies : le navigateur n'insiste pas avec un jeton mort.
        return sessions.close_session({"error": message}, status=401)

    @jwt.token_in_blocklist_loader
    def _is_revoked(_header, payload):
        return sessions.is_revoked(payload)

    @jwt.user_lookup_loader
    def _load_user(_header, payload):
        return db.session.get(User, int(payload["sub"]))

    @jwt.user_lookup_error_loader
    def _user_missing(_header, _payload):
        return refused("Compte introuvable.")

    @jwt.unauthorized_loader
    def _unauthorized(_reason):
        return jsonify({"error": "Connectez-vous pour continuer."}), 401

    @jwt.invalid_token_loader
    def _invalid(_reason):
        return refused("Session invalide, reconnectez-vous.")

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return refused("Session expirée, reconnectez-vous.")

    @jwt.revoked_token_loader
    def _revoked(_header, _payload):
        return refused("Session fermée, reconnectez-vous.")

    @app.errorhandler(CSRFError)
    def _csrf(_error):
        return jsonify({"error": "Requête refusée : jeton CSRF absent ou invalide."}), 403


def _register_guards(app: Flask) -> None:
    @app.before_request
    def _json_writes_only():
        # Un formulaire HTML d'un autre site ne peut pas envoyer du JSON sans
        # autorisation CORS (que l'API n'accorde à personne) : exiger ce type
        # de contenu ferme la porte aux requêtes forgées classiques.
        if (
            request.method in WRITE_METHODS
            and request.path.startswith("/api/")
            and request.mimetype != "application/json"
        ):
            return jsonify({"error": "Le corps de la requête doit être du JSON."}), 415
        return None

    @app.after_request
    def _security_headers(response):
        headers = response.headers
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Referrer-Policy", "no-referrer")
        headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        # L'API ne sert que du JSON : rien ne doit s'y exécuter ni s'y afficher.
        headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        # Les réponses contiennent des données personnelles : pas de cache.
        headers.setdefault("Cache-Control", "no-store")
        if request.is_secure:
            headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return response


def _register_errors(app: Flask) -> None:
    messages = {
        400: "Requête invalide.",
        404: "Ressource introuvable.",
        405: "Méthode non autorisée.",
        413: "Requête trop volumineuse.",
        415: "Format de requête non pris en charge.",
        429: "Trop de requêtes.",
    }

    def handler(code: int):
        def respond(_error):
            return jsonify({"error": messages[code]}), code
        return respond

    for code in messages:
        app.register_error_handler(code, handler(code))

    @app.errorhandler(500)
    def _server_error(error):  # pragma: no cover
        app.logger.exception("erreur serveur : %s", error)
        db.session.rollback()
        return jsonify({"error": "Erreur interne."}), 500
