"""Commandes d'administration : mots de passe, blocages, durées de conservation."""
from datetime import timedelta

from helpers import PASSWORD, login, register

from app.extensions import db
from app.models import RevokedToken, Throttle, User, utcnow


def test_set_password_ferme_les_sessions(app, client, auth):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["set-password", "ELEVE"], env={"NEW_PASSWORD": "tableau-noir-2026"})
    assert result.exit_code == 0, result.output

    assert client.get("/api/auth/me").status_code == 401
    assert login(app.test_client(), password=PASSWORD).status_code == 401
    assert login(app.test_client(), password="tableau-noir-2026").status_code == 200


def test_set_password_applique_la_politique(app, auth):
    result = app.test_cli_runner().invoke(args=["set-password", "eleve"], env={"NEW_PASSWORD": "court"})
    assert result.exit_code != 0
    assert "12 caractères" in result.output


def test_unlock_leve_un_blocage(app, client, auth):
    for _ in range(5):
        login(client, password="mauvais-passe-123")
    assert login(client).status_code == 429

    result = app.test_cli_runner().invoke(args=["unlock", "eleve@test.fr"])
    assert "Blocage levé" in result.output
    assert login(client).status_code == 200


def test_purge_applique_les_durees_de_conservation(app, client, auth):
    register(app.test_client(), username="ancien")
    ancien = User.query.filter_by(username="ancien").one()
    ancien.last_login_at = utcnow() - timedelta(days=30 * 25)
    db.session.add(RevokedToken(jti="expire", expires_at=utcnow() - timedelta(hours=1)))
    db.session.add(RevokedToken(jti="valide", expires_at=utcnow() + timedelta(hours=1)))
    db.session.add(Throttle(key="a" * 64, updated_at=utcnow() - timedelta(days=3)))
    db.session.commit()

    runner = app.test_cli_runner()
    assert "1 compte(s) inactif(s)" in runner.invoke(args=["purge", "--dry-run"]).output
    assert User.query.count() == 2

    result = runner.invoke(args=["purge"])
    assert result.exit_code == 0, result.output
    assert [user.username for user in User.query.all()] == ["eleve"]
    assert [token.jti for token in RevokedToken.query.all()] == ["valide"]
    assert Throttle.query.filter_by(key="a" * 64).count() == 0


def test_create_user_refuse_un_mot_de_passe_faible(app):
    runner = app.test_cli_runner()
    faible = runner.invoke(args=["create-user", "prof@test.fr", "prof"], env={"NEW_PASSWORD": "court"})
    assert faible.exit_code != 0

    solide = runner.invoke(args=["create-user", "prof@test.fr", "prof", "--admin"],
                           env={"NEW_PASSWORD": "tableau-noir-2026"})
    assert solide.exit_code == 0, solide.output
    assert User.query.filter_by(username="prof").one().is_admin is True
