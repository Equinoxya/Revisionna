import pytest

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
    """Cree un compte et renvoie l'en-tete d'autorisation."""
    resp = client.post("/api/auth/register", json={
        "email": "eleve@test.fr", "username": "eleve", "password": "motdepasse",
    })
    assert resp.status_code == 201, resp.get_json()
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
