"""Droits RGPD : rectification, export (accès et portabilité), effacement."""
import json

from helpers import PASSWORD, csrf, login, register

from app.models import Progress, Submission, User


def _travailler(client, auth):
    client.post("/api/courses/python/lessons/types-et-structures/complete",
                json={"answers": {"q1": "tuple"}}, headers=auth)
    exercise = client.get("/api/courses/sql/exercises/tp-jointure-notes").get_json()["exercise"]
    client.post(f"/api/exercises/{exercise['id']}/submit",
                json={"code": "SELECT titre FROM cours"}, headers=auth)


def test_export_contient_toutes_mes_donnees(client, auth):
    _travailler(client, auth)

    response = client.get("/api/me/export")
    assert response.status_code == 200
    assert "attachment" in response.headers["Content-Disposition"]

    document = json.loads(response.data)
    assert document["compte"]["email"] == "eleve@test.fr"
    assert document["compte"]["conditions_acceptees_le"]
    assert document["lecons_terminees"][0]["lecon"] == "types-et-structures"
    assert document["soumissions"][0]["reponse"] == "SELECT titre FROM cours"
    assert "password" not in response.get_data(as_text=True).lower()


def test_export_reserve_au_titulaire(client):
    assert client.get("/api/me/export").status_code == 401


def test_rectifier_son_profil(client, auth):
    response = client.patch("/api/me", headers=auth, json={
        "email": "Nouveau@Test.fr", "username": "Élève_2", "current_password": PASSWORD,
    })
    assert response.status_code == 200
    assert response.get_json()["user"] == {
        **response.get_json()["user"], "email": "nouveau@test.fr", "username": "Élève_2",
    }
    assert login(client.application.test_client(), "élève_2").status_code == 200


def test_rectification_exige_le_mot_de_passe(client, auth):
    response = client.patch("/api/me", headers=auth,
                            json={"email": "pirate@test.fr", "current_password": "pas-le-bon-123"})
    assert response.status_code == 403
    assert User.query.one().email == "eleve@test.fr"


def test_rectification_refuse_les_doublons(client, auth):
    register(client.application.test_client(), username="voisin")
    response = client.patch("/api/me", headers=auth,
                            json={"username": "VOISIN", "current_password": PASSWORD})
    assert response.status_code == 409


def test_supprimer_son_compte_efface_tout(client, auth):
    _travailler(client, auth)
    assert Progress.query.count() == 1 and Submission.query.count() == 1

    refuse = client.delete("/api/me", headers=auth, json={"password": "pas-le-bon-123"})
    assert refuse.status_code == 403
    assert User.query.count() == 1

    response = client.delete("/api/me", headers=auth, json={"password": PASSWORD})
    assert response.status_code == 200
    assert User.query.count() == 0
    assert Progress.query.count() == 0 and Submission.query.count() == 0

    assert client.get("/api/auth/me").status_code == 401
    assert login(client.application.test_client()).status_code == 401


def test_jeton_d_un_compte_supprime_inutilisable(client, auth):
    from helpers import SESSION_COOKIE, SESSION_PATH

    vole = client.get_cookie(SESSION_COOKIE, path=SESSION_PATH).value
    client.delete("/api/me", headers=auth, json={"password": PASSWORD})

    pirate = client.application.test_client()
    pirate.set_cookie(SESSION_COOKIE, vole, path=SESSION_PATH)
    assert pirate.get("/api/auth/me").status_code == 401


def test_meta_publique_sans_donnee_sensible(client, app):
    app.config["AI_PROVIDER"] = "openai"
    data = client.get("/api/meta").get_json()
    assert data["ai_external"] is True
    assert data["password_min_length"] == 12
    assert not any("key" in key.lower() or "secret" in key.lower() for key in data)


def test_changement_de_session_change_le_jeton_csrf(client, auth):
    login(client)
    assert csrf(client) != auth
