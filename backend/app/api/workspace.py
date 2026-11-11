"""Espace de travail : validation des leçons, soumission des TP, bulletin."""
from datetime import timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import func

from ..extensions import db
from ..models import Course, Exercise, Lesson, Progress, Submission
from ..services import activity, runner, throttle
from ..services.ai import AIUnavailable, ask, hint_prompt
from .common import body, too_many

bp = Blueprint("workspace", __name__, url_prefix="/api")

SUBMISSIONS_PER_MINUTE = 30
AI_REQUESTS_PER_10_MIN = 20


def ai_quota():
    """Le tuteur IA peut coûter de l'argent (API distante) : débit limité par compte."""
    return throttle.hit(
        "ai", current_user.id, limit=AI_REQUESTS_PER_10_MIN, window=timedelta(minutes=10)
    )


@bp.post("/courses/<course_slug>/lessons/<lesson_slug>/complete")
@jwt_required()
def complete_lesson(course_slug, lesson_slug):
    """Corrige les quiz de la leçon et enregistre la progression."""
    lesson = (
        Lesson.query.join(Course)
        .filter(Course.slug == course_slug, Lesson.slug == lesson_slug)
        .first()
    )
    if lesson is None:
        return jsonify({"error": "Leçon introuvable."}), 404

    answers = body().get("answers")
    answers = answers if isinstance(answers, dict) else {}

    details, ok = [], 0
    for quiz in lesson.quizzes:
        qid = str(quiz.get("id"))
        correct = answers.get(qid) == quiz.get("answer")
        ok += int(correct)
        details.append({
            "id": qid,
            "passed": correct,
            "answer": quiz.get("answer"),
            "explanation": quiz.get("explanation", ""),
        })
    score = round(ok / len(details), 3) if details else 1.0

    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    if progress is None:
        progress = Progress(user_id=current_user.id, lesson_id=lesson.id, quiz_score=score)
        db.session.add(progress)
    else:
        progress.quiz_score = max(progress.quiz_score or 0, score)
    db.session.commit()

    activity.log("lesson_completed", current_user.id, lesson=lesson.slug,
                 course=course_slug, score=score)
    return jsonify({"score": score, "results": details, "done": True})


@bp.get("/exercises/<int:exercise_id>/submissions")
@jwt_required()
def list_submissions(exercise_id):
    rows = (
        Submission.query.filter_by(user_id=current_user.id, exercise_id=exercise_id)
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

    wait = throttle.hit(
        "submit", current_user.id, limit=SUBMISSIONS_PER_MINUTE, window=timedelta(minutes=1)
    )
    if wait:
        return too_many(wait)

    data = body()
    spec = exercise.spec or {}

    if exercise.kind in ("python", "sql"):
        code = data.get("code")
        if not isinstance(code, str) or not code.strip():
            return jsonify({"error": "Votre réponse est vide."}), 400
        if len(code) > runner.MAX_CODE_CHARS:
            return jsonify({"error": "Votre réponse est trop longue."}), 413
        if exercise.kind == "python":
            result = runner.run_python(code, spec.get("tests", []))
        else:
            result = runner.run_sql(code, spec)
        stored = code
    elif exercise.kind == "quiz":
        answers = data.get("answers")
        answers = {str(k): v for k, v in answers.items()} if isinstance(answers, dict) else {}
        result = runner.run_quiz(answers, spec)
        stored = "\n".join(f"{qid} : {value}" for qid, value in sorted(answers.items()))
    else:
        return jsonify({"error": f"Type d'exercice inconnu : {exercise.kind}"}), 400

    submission = Submission(
        user_id=current_user.id, exercise_id=exercise.id, code=stored,
        passed=result["passed"], score=result["score"], output=result.get("output", ""),
    )
    db.session.add(submission)
    db.session.commit()

    activity.log("exercise_submitted", current_user.id, exercise=exercise.slug,
                 passed=result["passed"], score=result["score"])

    payload = {
        "passed": result["passed"],
        "score": result["score"],
        "output": result.get("output", ""),
        "results": result.get("results", []),
        "submission_id": submission.id,
    }
    for key in ("stdout", "columns", "rows", "expected_rows"):
        if key in result:
            payload[key] = result[key]
    if result["passed"] and exercise.solution:
        payload["solution"] = exercise.solution
    return jsonify(payload)


@bp.post("/exercises/<int:exercise_id>/hint")
@jwt_required()
def exercise_hint(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercice introuvable."}), 404

    wait = ai_quota()
    if wait:
        return too_many(wait)

    data = body()
    code = data.get("code") if isinstance(data.get("code"), str) else ""
    output = data.get("output") if isinstance(data.get("output"), str) else ""
    try:
        answer = ask(hint_prompt(exercise, code, output))
    except AIUnavailable as exc:
        static = exercise.hints or []
        return jsonify({
            "provider": "secours",
            "answer": static[0] if static else "Le tuteur est indisponible pour le moment.",
            "warning": str(exc),
        })

    activity.log("hint_requested", current_user.id, exercise=exercise.slug)
    return jsonify(answer)


@bp.get("/me/dashboard")
@jwt_required()
def dashboard():
    """Le bulletin : avancement et moyenne par cours."""
    uid = current_user.id
    courses = Course.query.order_by(Course.position).all()

    quiz_scores = {row.lesson_id: row.quiz_score or 0.0
                   for row in Progress.query.filter_by(user_id=uid)}
    best = dict(
        db.session.query(Submission.exercise_id, func.max(Submission.score))
        .filter_by(user_id=uid)
        .group_by(Submission.exercise_id)
        .all()
    )
    passed = {
        row.exercise_id
        for row in db.session.query(Submission.exercise_id)
        .filter_by(user_id=uid, passed=True)
        .distinct()
    }

    per_course, every_score = [], []
    for course in courses:
        lesson_ids = {lesson.id for lesson in course.lessons}
        exercise_ids = {exercise.id for exercise in course.exercises}
        # Ne comptent dans la moyenne que les travaux réellement notés :
        # quiz des leçons terminées, meilleure tentative de chaque TP essayé.
        scores = [quiz_scores[lesson.id] for lesson in course.lessons
                  if lesson.id in quiz_scores and lesson.quizzes]
        scores += [best[exercise_id] or 0.0 for exercise_id in exercise_ids if exercise_id in best]
        every_score += scores
        per_course.append({
            "slug": course.slug,
            "title": course.title,
            "icon": course.icon,
            "category": course.category,
            "position": course.position,
            "lessons_total": len(lesson_ids),
            "lessons_done": len(lesson_ids & quiz_scores.keys()),
            "exercises_total": len(exercise_ids),
            "exercises_passed": len(exercise_ids & passed),
            "average": round(sum(scores) / len(scores), 3) if scores else None,
        })

    recent = (
        Submission.query.filter_by(user_id=uid)
        .order_by(Submission.created_at.desc())
        .limit(8)
        .all()
    )
    return jsonify({
        "totals": {
            "lessons_done": len(quiz_scores),
            "lessons_total": sum(item["lessons_total"] for item in per_course),
            "exercises_passed": len(passed),
            "exercises_total": sum(item["exercises_total"] for item in per_course),
            "submissions": Submission.query.filter_by(user_id=uid).count(),
            "average": round(sum(every_score) / len(every_score), 3) if every_score else None,
        },
        "courses": per_course,
        "recent_submissions": [row.to_dict() for row in recent],
    })
