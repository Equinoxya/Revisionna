"""Comptes et sessions : inscription, connexion, déconnexion, mot de passe."""
from datetime import timedelta

import pytest
from helpers import PASSWORD, SESSION_COOKIE, SESSION_PATH, csrf, login, register

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Throttle, User, utcnow
from app.services import passwords, throttle

# --- Inscription -------------------------------------------------------------

def test_inscription_ouvre_une_session_par_cookie(client):
    response = register(client, username="Alice", email="Alice@Test.fr")
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["email"] == "alice@test.fr"
    assert "access_token" not in data          # le jeton ne transite pas par JavaScript

    cookies = response.headers.getlist("Set-Cookie")
    session = next(c for c in cookies if c.startswith(SESSION_COOKIE))
    assert "HttpOnly" in session
    assert "SameSite=Strict" in session
    assert "Path=/api/" in session

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.get_json()["user"]["username"] == "Alice"


def test_inscription_enregistre_l_acceptation_des_conditions(client, app):
    register(client)
    user = User.query.filter_by(email="eleve@test.fr").one()
    assert user.terms_accepted_at is not None
    assert user.terms_version == app.config["TERMS_VERSION"]


def test_inscription_invalide(client):
    response = client.post("/api/auth/register", json={
        "email": "pasunemail", "username": "ab", "password": "court",
    })
    assert response.status_code == 400
    assert set(response.get_json()["errors"]) == {"email", "username", "password", "accept_terms"}


@pytest.mark.parametrize("password, fragment", [
    ("court1", "12 caractères"),
    ("uniquementdeslettres", "une lettre et un chiffre"),
    ("123456789012345", "une lettre et un chiffre"),
    ("motdepasse123", "trop courant"),
    ("aaaaaaaaaaa1", "trop courant"),
    ("superEleve2026", "nom d'utilisateur"),
])
def test_politique_de_mot_de_passe(client, password, fragment):
    response = register(client, password=password)
    assert response.status_code == 400
    assert fragment in response.get_json()["errors"]["password"]


def test_pseudo_avec_arobase_refuse(client):
    # Sinon un pseudo pourrait imiter l'email d'un autre compte à la connexion.
    response = register(client, username="victime@test.fr", email="pirate@test.fr")
    assert response.status_code == 400
    assert "username" in response.get_json()["errors"]


def test_doublons_refuses_sans_tenir_compte_de_la_casse(client, auth):
    autre = client.application.test_client()
    assert register(autre, username="autre", email="ELEVE@test.fr").status_code == 409
    response = register(autre, username="ELEVE", email="autre@test.fr")
    assert response.status_code == 409
    assert "username" in response.get_json()["errors"]


def test_code_d_invitation(app, client):
    app.config["INVITE_CODE"] = "promo-2026"
    assert register(client).status_code == 400
    assert register(client, invite_code="faux").get_json()["errors"]["invite_code"]
    assert register(client, invite_code="promo-2026").status_code == 201


# --- Connexion ---------------------------------------------------------------

def test_connexion_par_email_ou_pseudo_quelle_que_soit_la_casse(client):
    register(client, username="Ophélie", email="ophelie@test.fr")
    for identifier in ("ophelie@test.fr", "OPHELIE@TEST.FR", "Ophélie", "ophélie", "OPHÉLIE"):
        frais = client.application.test_client()
        assert login(frais, identifier).status_code == 200, identifier


def test_mauvais_identifiants_meme_reponse(client, auth):
    inconnu = login(client, "personne@test.fr", "peu-importe-123")
    mauvais = login(client, "eleve@test.fr", "peu-importe-123")
    assert inconnu.status_code == mauvais.status_code == 401
    assert inconnu.get_json() == mauvais.get_json()


def test_compte_inexistant_verifie_quand_meme_un_mot_de_passe(monkeypatch):
    # Sans ce leurre, une réponse immédiate révélerait que le compte n'existe pas.
    appels = []
    monkeypatch.setattr(passwords, "check_password_hash",
                        lambda stored, given: appels.append(stored) or False)
    assert passwords.verify(None, "nimporte-quoi-1") is False
    assert len(appels) == 1


def test_route_protegee_sans_session(client):
    assert client.get("/api/me/dashboard").status_code == 401
    assert client.get("/api/auth/me").status_code == 401


# --- Protection contre les requêtes forgées -----------------------------------

def test_ecriture_sans_jeton_csrf_refusee(client, auth):
    assert client.post("/api/auth/password", json={}).status_code == 403
    assert client.post("/api/auth/password", json={}, headers={"X-CSRF-Token": "faux"}).status_code == 403


def test_ecriture_hors_json_refusee(client, auth):
    response = client.post("/api/auth/login", data={"identifier": "x", "password": "y"})
    assert response.status_code == 415


# --- Déconnexion -------------------------------------------------------------

def test_deconnexion_revoque_le_jeton_en_base(client, auth):
    vole = client.get_cookie(SESSION_COOKIE, path=SESSION_PATH).value

    response = client.post("/api/auth/logout", json={}, headers=auth)
    assert response.status_code == 200
    assert client.get_cookie(SESSION_COOKIE, path=SESSION_PATH) is None
    assert client.get("/api/auth/me").status_code == 401

    # Un jeton copié avant la déconnexion ne sert plus à rien, quel que soit le worker.
    pirate = client.application.test_client()
    pirate.set_cookie(SESSION_COOKIE, vole, path=SESSION_PATH)
    assert pirate.get("/api/auth/me").status_code == 401


def test_deconnexion_sans_session_ne_plante_pas(client):
    assert client.post("/api/auth/logout", json={}).status_code == 200


# --- Temporisation après échecs ------------------------------------------------

def echouer(client, fois, identifier="eleve@test.fr"):
    return [login(client, identifier, "mauvais-mot-de-passe-1").status_code for _ in range(fois)]


def test_blocage_apres_cinq_echecs_meme_avec_le_bon_mot_de_passe(client, auth):
    assert echouer(client, 5) == [401] * 5

    bloque = login(client)                       # bon mot de passe, mais trop tard
    assert bloque.status_code == 429
    assert 0 < int(bloque.headers["Retry-After"]) <= 60
    assert "Réessayez dans" in bloque.get_json()["error"]


def test_blocage_identique_pour_un_compte_inexistant(client):
    # Sinon le blocage lui-même révélerait quels comptes existent.
    assert echouer(client, 5, "fantome@test.fr") == [401] * 5
    assert login(client, "fantome@test.fr").status_code == 429


def test_attente_qui_double_puis_plafonne(app):
    attentes = []
    for _ in range(12):
        throttle.login_failed("cible")
        attentes.append(throttle.login_wait("cible"))
    assert attentes[:4] == [None] * 4
    assert [round(a / 60) for a in attentes[4:9]] == [1, 2, 4, 8, 15]
    assert all(a <= throttle.MAX_DELAY for a in attentes[4:])


def test_plafond_quotidien(app):
    for _ in range(throttle.DAILY_FAILURES):
        throttle.login_failed("cible")
    assert throttle.login_wait("cible") > 20 * 3600


def test_connexion_reussie_remet_le_compteur_a_zero(client, auth):
    echouer(client, 4)
    assert login(client).status_code == 200
    assert echouer(client, 4) == [401] * 4      # pas de blocage au 5e échec cumulé


def test_fin_d_attente_autorise_un_nouvel_essai(client, auth):
    echouer(client, 5)
    row = Throttle.query.filter(Throttle.blocked_until.isnot(None)).one()
    row.blocked_until = utcnow() - timedelta(seconds=1)
    db.session.commit()
    assert login(client).status_code == 200


def test_plafond_par_adresse_ip(client, auth, monkeypatch):
    from app.api import auth as auth_api

    monkeypatch.setattr(auth_api, "LOGIN_FAILURES_PER_IP", 3)
    codes = [login(client, f"compte{i}@test.fr", "mauvais-passe-12").status_code for i in range(4)]
    assert codes == [401, 401, 401, 429]


def test_compteurs_sans_donnee_en_clair(client, auth):
    echouer(client, 2)
    for row in Throttle.query.all():
        assert len(row.key) == 64 and "eleve" not in row.key and "127.0.0.1" not in row.key


# --- Changement de mot de passe -------------------------------------------------

def test_changer_de_mot_de_passe_ferme_les_autres_sessions(client, auth):
    autre_appareil = client.application.test_client()
    assert login(autre_appareil).status_code == 200

    nouveau = "nouvelle-ardoise-77"
    response = client.post("/api/auth/password", headers=auth,
                           json={"current_password": PASSWORD, "new_password": nouveau})
    assert response.status_code == 200

    assert client.get("/api/auth/me").status_code == 200           # cet appareil reste connecté
    assert autre_appareil.get("/api/auth/me").status_code == 401   # l'autre est déconnecté
    assert login(client.application.test_client(), password=PASSWORD).status_code == 401
    assert login(client.application.test_client(), password=nouveau).status_code == 200


def test_changement_refuse_si_mot_de_passe_actuel_faux(client, auth):
    response = client.post("/api/auth/password", headers=auth,
                           json={"current_password": "pas-le-bon-123", "new_password": "nouvelle-ardoise-77"})
    assert response.status_code == 403
    assert "current_password" in response.get_json()["errors"]


def test_nouveau_mot_de_passe_soumis_a_la_politique(client, auth):
    for nouveau in ("court1", PASSWORD):
        response = client.post("/api/auth/password", headers=csrf(client),
                               json={"current_password": PASSWORD, "new_password": nouveau})
        assert response.status_code == 400


def test_verification_du_mot_de_passe_actuel_limitee(client, auth):
    codes = [
        client.post("/api/auth/password", headers=auth,
                    json={"current_password": "faux-passe-1234", "new_password": "x"}).status_code
        for _ in range(6)
    ]
    assert codes == [403] * 5 + [429]


# --- Configuration et en-têtes --------------------------------------------------

def test_en_tetes_de_securite(client):
    headers = client.get("/api/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Cache-Control"] == "no-store"
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert "Access-Control-Allow-Origin" not in headers


def test_aucune_origine_tierce_autorisee(client):
    response = client.get("/api/health", headers={"Origin": "https://site-malveillant.example"})
    assert "Access-Control-Allow-Origin" not in response.headers


@pytest.mark.parametrize("secret", ["", "trop-court", "change-me-en-production-0123456789abcdef"])
def test_production_refuse_les_secrets_faibles(secret):
    class Production(TestConfig):
        TESTING = False
        PRODUCTION = True
        SECRET_KEY = secret

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(Production)


def test_production_accepte_des_secrets_solides():
    class Production(TestConfig):
        TESTING = False
        PRODUCTION = True
        JWT_COOKIE_SECURE = True

    assert create_app(Production).config["JWT_COOKIE_SECURE"] is True


def test_cookies_marques_secure_des_que_la_requete_arrive_en_https(client):
    # COOKIE_SECURE est désactivé dans les tests : en HTTP le drapeau est absent…
    en_clair = register(client, username="clair").headers.getlist("Set-Cookie")
    assert not any("Secure" in cookie for cookie in en_clair)

    # … mais en HTTPS il est ajouté d'office, session comme jeton CSRF.
    https = client.application.test_client()
    chiffre = https.post("/api/auth/login", base_url="https://localhost",
                         json={"identifier": "clair", "password": PASSWORD})
    cookies = chiffre.headers.getlist("Set-Cookie")
    assert len(cookies) == 2 and all("; Secure" in cookie for cookie in cookies)
    assert chiffre.headers["Strict-Transport-Security"]
