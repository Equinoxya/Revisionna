"""Espace de travail de l'eleve : validation des lecons, soumission des TP, progression."""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Course, Exercise, Lesson, Progress, Submission
from ..services import activity, runner
from ..services.ai import AIUnavailable, ask, hint_prompt

bp = Blueprint("workspace", __name__, url_prefix="/api")


def _uid() -> int:
    return int(get_jwt_identity())


@bp.post("/courses/<course_slug>/lessons/<lesson_slug>/complete")
@jwt_required()
def complete_lesson(course_slug, lesson_slug):
    """Corrige les quiz de la lecon et enregistre la progression."""
    lesson = (
        Lesson.query.join(Course)
        .filter(Course.slug == course_slug, Lesson.slug == lesson_slug)
        .first()
    )
    if lesson is None:
        return jsonify({"error": "Lecon introuvable."}), 404

    answers = (request.get_json(silent=True) or {}).get("answers", {}) or {}
    quizzes = [b for b in (lesson.blocks or []) if b.get("type") == "quiz"]
    details, ok = [], 0
    for quiz in quizzes:
        qid = str(quiz.get("id"))
        correct = answers.get(qid) == quiz.get("answer")
        ok += int(correct)
        details.append({
            "id": qid,
            "passed": correct,
            "answer": quiz.get("answer"),
            "explanation": quiz.get("explanation", ""),
        })
    score = round(ok / len(quizzes), 3) if quizzes else 1.0

    progress = Progress.query.filter_by(user_id=_uid(), lesson_id=lesson.id).first()
    if progress is None:
        progress = Progress(user_id=_uid(), lesson_id=lesson.id, quiz_score=score)
        db.session.add(progress)
    else:
        progress.quiz_score = max(progress.quiz_score or 0, score)
    db.session.commit()

    activity.log("lesson_completed", _uid(), lesson=lesson.slug,
                 course=course_slug, score=score)
    return jsonify({"score": score, "results": details, "done": True})


@bp.get("/exercises/<int:exercise_id>/submissions")
@jwt_required()
def list_submissions(exercise_id):
    rows = (
        Submission.query.filter_by(user_id=_uid(), exercise_id=exercise_id)
        .order_by(Submission.created_at.desc())
        .limit(10)
        .all()
    )
    return jsonify({"submissions": [
        {**row.to_dict(), "code": row.code, "output": row.output} for row in rows
    ]})


@bp.post("/exercises/<int:exercise_id>/submit")
@jwt_required()
def submit_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercice introuvable."}), 404

    body = request.get_json(silent=True) or {}
    spec = exercise.spec or {}

    if exercise.kind == "python":
        code = body.get("code") or ""
        if not code.strip():
            return jsonify({"error": "Code vide."}), 400
        result = runner.run_python(
            code, spec.get("tests", []), timeout=current_app.config["RUNNER_TIMEOUT"]
        )
        stored = code
    elif exercise.kind == "sql":
        code = body.get("code") or ""
        if not code.strip():
            return jsonify({"error": "Requete vide."}), 400
        result = runner.run_sql(code, spec)
        stored = code
    elif exercise.kind == "quiz":
        answers = {str(k): v for k, v in (body.get("answers") or {}).items()}
        result = runner.run_quiz(answers, spec)
        stored = repr(answers)
    else:
        return jsonify({"error": f"Type d'exercice inconnu : {exercise.kind}"}), 400

    submission = Submission(
        user_id=_uid(), exercise_id=exercise.id, code=stored,
        passed=result["passed"], score=result["score"], output=result.get("output", ""),
    )
    db.session.add(submission)
    db.session.commit()

    activity.log("exercise_submitted", _uid(), exercise=exercise.slug,
                 passed=result["passed"], score=result["score"])

    payload = {
        "passed": result["passed"],
        "score": result["score"],
        "output": result.get("output", ""),
        "results": result.get("results", []),
        "submission_id": submission.id,
    }
    if result["passed"] and exercise.solution:
        payload["solution"] = exercise.solution
    return jsonify(payload)


@bp.post("/exercises/<int:exercise_id>/hint")
@jwt_required()
def exercise_hint(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercice introuvable."}), 404

    body = request.get_json(silent=True) or {}
    try:
        answer = ask(hint_prompt(exercise, body.get("code", ""), body.get("output", "")))
    except AIUnavailable as exc:
        static = (exercise.hints or [])
        return jsonify({
            "provider": "fallback",
            "answer": static[0] if static else str(exc),
            "warning": str(exc),
        }), 200

    activity.log("hint_requested", _uid(), exercise=exercise.slug)
    return jsonify(answer)


@bp.get("/me/dashboard")
@jwt_required()
def dashboard():
    uid = _uid()
    courses = Course.query.order_by(Course.position).all()
    done_lessons = {p.lesson_id for p in Progress.query.filter_by(user_id=uid)}
    passed_ex = {
        s.exercise_id
        for s in Submission.query.filter_by(user_id=uid, passed=True)
    }

    per_course = []
    for course in courses:
        lesson_ids = {lesson.id for lesson in course.lessons}
        ex_ids = {ex.id for ex in course.exercises}
        per_course.append({
            "slug": course.slug,
            "title": course.title,
            "icon": course.icon,
            "lessons_total": len(lesson_ids),
            "lessons_done": len(lesson_ids & done_lessons),
            "exercises_total": len(ex_ids),
            "exercises_passed": len(ex_ids & passed_ex),
        })

    recent = (
        Submission.query.filter_by(user_id=uid)
        .order_by(Submission.created_at.desc())
        .limit(8)
        .all()
    )
    return jsonify({
        "totals": {
            "lessons_done": len(done_lessons),
            "exercises_passed": len(passed_ex),
            "submissions": Submission.query.filter_by(user_id=uid).count(),
        },
        "courses": per_course,
        "recent_submissions": [row.to_dict() for row in recent],
        "activity": activity.recent(uid, limit=10),
    })
