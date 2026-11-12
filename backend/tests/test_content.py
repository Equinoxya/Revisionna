def test_catalogue_public(client):
    resp = client.get("/api/courses")
    assert resp.status_code == 200
    courses = resp.get_json()["courses"]
    assert len(courses) == 14
    slugs = {c["slug"] for c in courses}
    assert {"python", "flask", "django", "react", "sql", "nosql",
            "machine-learning", "integration-ia", "docker", "ci-cd",
            "deploiement", "devops-bases", "systeme-linux", "reseaux"} == slugs


def test_detail_cours(client):
    resp = client.get("/api/courses/python")
    assert resp.status_code == 200
    course = resp.get_json()["course"]
    assert course["lessons"] and course["exercises"]


def test_cours_inconnu(client):
    assert client.get("/api/courses/perl").status_code == 404


def test_lecon_sans_reponses_de_quiz(client, auth):
    resp = client.get("/api/courses/python/lessons/types-et-structures", headers=auth)
    assert resp.status_code == 200
    blocks = resp.get_json()["lesson"]["blocks"]
    quiz = [b for b in blocks if b["type"] == "quiz"]
    assert quiz, "la lecon doit contenir un quiz"
    for block in quiz:
        assert "answer" not in block
        assert "explanation" not in block


def test_exercice_sans_solution(client, auth):
    resp = client.get("/api/courses/python/exercises/tp-statistiques", headers=auth)
    assert resp.status_code == 200
    exercise = resp.get_json()["exercise"]
    assert "solution" not in exercise
    assert exercise["spec"]["tests"]  # seulement les noms des tests


def test_lecon_requiert_authentification(client):
    assert client.get("/api/courses/python/lessons/types-et-structures").status_code == 401


def test_lecon_commence_par_sa_video(client, auth):
    resp = client.get("/api/courses/reseaux/lessons/ports-dns-et-dhcp", headers=auth)
    assert resp.status_code == 200
    blocks = resp.get_json()["lesson"]["blocks"]
    assert blocks[0] == {"type": "video", "url": ""}
