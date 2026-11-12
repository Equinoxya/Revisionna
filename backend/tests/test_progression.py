def test_valider_une_lecon_avec_quiz(client, auth):
    resp = client.get("/api/courses/python/lessons/types-et-structures", headers=auth)
    blocks = resp.get_json()["lesson"]["blocks"]
    quiz_ids = [b["id"] for b in blocks if b["type"] == "quiz"]

    # reponses volontairement fausses
    fausses = {qid: "reponse bidon" for qid in quiz_ids}
    resp = client.post(
        "/api/courses/python/lessons/types-et-structures/complete",
        json={"answers": fausses}, headers=auth,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["score"] == 0.0
    assert data["done"] is True
    # la correction est renvoyee apres validation
    assert all(d["answer"] for d in data["results"])


def test_bonnes_reponses_donnent_un_score_parfait(client, auth, app):
    from app.models import Course, Lesson

    with app.app_context():
        lesson = (
            Lesson.query.join(Course)
            .filter(Course.slug == "python", Lesson.slug == "types-et-structures")
            .first()
        )
        bonnes = {b["id"]: b["answer"] for b in lesson.blocks if b["type"] == "quiz"}

    resp = client.post(
        "/api/courses/python/lessons/types-et-structures/complete",
        json={"answers": bonnes}, headers=auth,
    )
    assert resp.get_json()["score"] == 1.0


def test_progression_visible_dans_le_tableau_de_bord(client, auth):
    client.post("/api/courses/python/lessons/types-et-structures/complete",
                json={"answers": {}}, headers=auth)

    resp = client.get("/api/me/dashboard", headers=auth)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["totals"]["lessons_done"] == 1
    python = next(c for c in data["courses"] if c["slug"] == "python")
    assert python["lessons_done"] == 1
    assert python["lessons_total"] == 4


def test_validation_idempotente(client, auth):
    for _ in range(3):
        client.post("/api/courses/python/lessons/types-et-structures/complete",
                    json={"answers": {}}, headers=auth)
    data = client.get("/api/me/dashboard", headers=auth).get_json()
    assert data["totals"]["lessons_done"] == 1


def test_lecon_marquee_faite_dans_le_detail_du_cours(client, auth):
    client.post("/api/courses/python/lessons/types-et-structures/complete",
                json={"answers": {}}, headers=auth)
    course = client.get("/api/courses/python", headers=auth).get_json()["course"]
    premiere = next(item for item in course["lessons"] if item["slug"] == "types-et-structures")
    assert premiere["done"] is True


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["database"] == "ok"


def test_moyenne_du_bulletin(client, auth, app):
    from app.models import Course, Exercise

    # leçon : 1 bonne réponse sur 2 -> 0,5 ; TP : solution de référence -> 1,0
    client.post("/api/courses/python/lessons/types-et-structures/complete",
                json={"answers": {"q1": "tuple", "q2": "faux"}}, headers=auth)
    with app.app_context():
        exercise = (Exercise.query.join(Course)
                    .filter(Course.slug == "python", Exercise.slug == "tp-statistiques").one())
        ex_id, solution = exercise.id, exercise.solution
    client.post(f"/api/exercises/{ex_id}/submit", json={"code": "x = 1"}, headers=auth)
    client.post(f"/api/exercises/{ex_id}/submit", json={"code": solution}, headers=auth)

    data = client.get("/api/me/dashboard").get_json()
    python = next(c for c in data["courses"] if c["slug"] == "python")
    assert python["average"] == 0.75           # (0,5 + 1,0) / 2 : la meilleure tentative compte
    assert python["exercises_passed"] == 1
    flask = next(c for c in data["courses"] if c["slug"] == "flask")
    assert flask["average"] is None            # rien de noté : pas de moyenne
    assert data["totals"]["average"] == 0.75


def test_dates_serialisees_avec_fuseau(client, auth):
    user = client.get("/api/auth/me").get_json()["user"]
    assert user["created_at"].endswith("+00:00")
