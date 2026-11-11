"""Fabrique d'application Flask (application factory pattern)."""
import logging

from flask import Flask, jsonify

from .config import Config
from .extensions import db, jwt, migrate


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    logging.basicConfig(level=logging.INFO)

    from .api import auth, content, system, workspace

    app.register_blueprint(auth.bp)
    app.register_blueprint(content.bp)
    app.register_blueprint(workspace.bp)
    app.register_blueprint(system.bp)

    from .api.auth import REVOKED

    @jwt.token_in_blocklist_loader
    def _revoked(_header, payload):
        return payload["jti"] in REVOKED

    @jwt.unauthorized_loader
    def _unauthorized(reason):
        return jsonify({"error": "Authentification requise.", "detail": reason}), 401

    @jwt.invalid_token_loader
    def _invalid(reason):
        return jsonify({"error": "Jeton invalide.", "detail": reason}), 401

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return jsonify({"error": "Session expiree, reconnectez-vous."}), 401

    @jwt.revoked_token_loader
    def _revoked_resp(_header, _payload):
        return jsonify({"error": "Session fermee."}), 401

    @app.errorhandler(404)
    def _not_found(_err):
        return jsonify({"error": "Ressource introuvable."}), 404

    @app.errorhandler(500)
    def _server_error(err):  # pragma: no cover
        app.logger.exception("Erreur serveur : %s", err)
        return jsonify({"error": "Erreur interne."}), 500

    from . import cli

    cli.register(app)
    return app
