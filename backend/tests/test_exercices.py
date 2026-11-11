from app.models import Course, Exercise


def _exercice(slug_cours, slug_ex):
    return (
        Exercise.query.join(Course)
        .filter(Course.slug == slug_cours, Exercise.slug == slug_ex)
        .first()
    )


def test_soumission_python_correcte(client, auth, app):
    with app.app_context():
        exercise = _exercice("python", "tp-statistiques")
        code = exercise.solution
        ex_id = exercise.id

    resp = client.post(f"/api/exercises/{ex_id}/submit", json={"code": code}, headers=auth)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["passed"] is True
    assert data["score"] == 1.0
    assert "solution" in data


def test_soumission_python_incorrecte(client, auth, app):
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    code = "def moyenne(notes):\n    return 42\n\ndef admis(notes, seuil=10):\n    return []\n\ndef repartition(notes):\n    return {}\n"
    resp = client.post(f"/api/exercises/{ex_id}/submit", json={"code": code}, headers=auth)
    data = resp.get_json()
    assert data["passed"] is False
    assert data["score"] < 1.0
    assert "solution" not in data


def test_code_eleve_sans_acces_aux_secrets(client, auth, app, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "ne-doit-pas-fuiter")
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    resp = client.post(
        f"/api/exercises/{ex_id}/submit",
        json={"code": "import os\nprint(dict(os.environ))\n"},
        headers=auth,
    )
    data = resp.get_json()
    assert "ne-doit-pas-fuiter" not in str(data)


def test_code_trop_long_refuse(client, auth, app):
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    resp = client.post(f"/api/exercises/{ex_id}/submit",
                       json={"code": "x = 1\n" * 10_000}, headers=auth)
    assert resp.status_code == 413


def test_boucle_infinie_interrompue(client, auth, app):
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    resp = client.post(
        f"/api/exercises/{ex_id}/submit",
        json={"code": "while True:\n    pass\n"},
        headers=auth,
    )
    data = resp.get_json()
    assert data["passed"] is False
    assert "interrompue" in data["output"] or "Temps dépassé" in data["output"]


def test_soumission_sql(client, auth, app):
    with app.app_context():
        exercise = _exercice("sql", "tp-jointure-notes")
        solution, ex_id = exercise.solution, exercise.id

    assert client.post(f"/api/exercises/{ex_id}/submit", json={"code": solution},
                       headers=auth).get_json()["passed"] is True

    mauvaise = client.post(f"/api/exercises/{ex_id}/submit",
                           json={"code": "SELECT titre FROM cours"}, headers=auth)
    assert mauvaise.get_json()["passed"] is False


def test_sql_invalide_renvoie_message(client, auth, app):
    with app.app_context():
        ex_id = _exercice("sql", "tp-jointure-notes").id

    resp = client.post(f"/api/exercises/{ex_id}/submit",
                       json={"code": "SELECT * FROM table_inexistante"}, headers=auth)
    data = resp.get_json()
    assert data["passed"] is False
    assert "erreur sql" in data["output"].lower()


def test_soumission_quiz(client, auth, app):
    with app.app_context():
        exercise = _exercice("docker", "quiz-docker")
        bonnes = {q["id"]: q["answer"] for q in exercise.spec["questions"]}
        ex_id = exercise.id

    resp = client.post(f"/api/exercises/{ex_id}/submit", json={"answers": bonnes}, headers=auth)
    assert resp.get_json()["passed"] is True

    partiel = dict(bonnes)
    partiel["1"] = "n'importe quoi"
    data = client.post(f"/api/exercises/{ex_id}/submit",
                       json={"answers": partiel}, headers=auth).get_json()
    assert data["passed"] is False
    assert 0 < data["score"] < 1


def test_historique_des_soumissions(client, auth, app):
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    client.post(f"/api/exercises/{ex_id}/submit", json={"code": "x = 1"}, headers=auth)
    resp = client.get(f"/api/exercises/{ex_id}/submissions", headers=auth)
    assert resp.status_code == 200
    assert len(resp.get_json()["submissions"]) == 1


def test_indice_sans_fournisseur_ia(client, auth, app):
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    resp = client.post(f"/api/exercises/{ex_id}/hint",
                       json={"code": "x = 1", "output": "FAIL"}, headers=auth)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["provider"] == "offline"
    assert data["answer"]


def test_exercice_inexistant(client, auth):
    assert client.post("/api/exercises/9999/submit", json={"code": "x = 1"},
                       headers=auth).status_code == 404


def test_debit_des_soumissions_limite(client, auth, app, monkeypatch):
    from app.api import workspace

    monkeypatch.setattr(workspace, "SUBMISSIONS_PER_MINUTE", 2)
    with app.app_context():
        ex_id = _exercice("docker", "quiz-docker").id

    codes = [client.post(f"/api/exercises/{ex_id}/submit", json={"answers": {}},
                         headers=auth).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_correction_refusee_sans_executeur_isole_en_production(client, auth, app):
    app.config["ALLOW_LOCAL_RUNNER"] = False
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    data = client.post(f"/api/exercises/{ex_id}/submit", json={"code": "x = 1"},
                       headers=auth).get_json()
    assert data["passed"] is False
    assert "désactivée" in data["output"]


def test_service_de_correction_injoignable_signale(client, auth, app, tmp_path):
    app.config["RUNNER_SOCKET"] = str(tmp_path / "absent.sock")
    with app.app_context():
        ex_id = _exercice("python", "tp-statistiques").id

    data = client.post(f"/api/exercises/{ex_id}/submit", json={"code": "x = 1"},
                       headers=auth).get_json()
    assert data["passed"] is False
    assert "indisponible" in data["output"]
