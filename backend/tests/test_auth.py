def test_inscription_puis_profil(client):
    resp = client.post("/api/auth/register", json={
        "email": "Alice@Test.fr", "username": "alice", "password": "motdepasse",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user"]["email"] == "alice@test.fr"

    headers = {"Authorization": f"Bearer {data['access_token']}"}
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.get_json()["user"]["username"] == "alice"


def test_inscription_invalide(client):
    resp = client.post("/api/auth/register", json={
        "email": "pasunemail", "username": "ab", "password": "court",
    })
    assert resp.status_code == 400
    assert set(resp.get_json()["errors"]) == {"email", "username", "password"}


def test_inscription_doublon(client, auth):
    resp = client.post("/api/auth/register", json={
        "email": "eleve@test.fr", "username": "autre", "password": "motdepasse",
    })
    assert resp.status_code == 409


def test_connexion_et_deconnexion(client, auth):
    resp = client.post("/api/auth/login", json={
        "email": "eleve@test.fr", "password": "motdepasse",
    })
    assert resp.status_code == 200
    headers = {"Authorization": f"Bearer {resp.get_json()['access_token']}"}

    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    # le jeton revoque ne passe plus
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_connexion_par_username(client, auth):
    resp = client.post("/api/auth/login", json={
        "username": "eleve", "password": "motdepasse",
    })
    assert resp.status_code == 200


def test_mauvais_mot_de_passe(client, auth):
    resp = client.post("/api/auth/login", json={
        "email": "eleve@test.fr", "password": "faux",
    })
    assert resp.status_code == 401


def test_route_protegee_sans_jeton(client):
    assert client.get("/api/me/dashboard").status_code == 401
