import pytest
from helpers import csrf, register

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.seed import load


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        load()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth(client):
    """Ouvre une session (cookie dans le client) et renvoie l'en-tête CSRF."""
    response = register(client)
    assert response.status_code == 201, response.get_json()
    return csrf(client)
