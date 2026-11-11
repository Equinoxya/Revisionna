"""Cours, leçons interactives, énoncés d'exercices."""
from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required

from ..models import Course, Exercise, Lesson, Progress

bp = Blueprint("content", __name__, url_prefix="/api")


def _done_lessons() -> set[int]:
    if not current_user:
        return set()
    return {row.lesson_id for row in Progress.query.filter_by(user_id=current_user.id)}


@bp.get("/courses")
@jwt_required(optional=True)
def list_courses():
    done = _done_lessons()
    payload = []
    for course in Course.query.order_by(Course.position).all():
        data = course.to_dict()
        data["lessons_done"] = len({lesson.id for lesson in course.lessons} & done)
        payload.append(data)
    return jsonify({"courses": payload})


@bp.get("/courses/<slug>")
@jwt_required(optional=True)
def get_course(slug):
    course = Course.query.filter_by(slug=slug).first()
    if course is None:
        return jsonify({"error": "Cours introuvable."}), 404

    done = _done_lessons()
    data = course.to_dict(with_children=True)
    for lesson in data["lessons"]:
        lesson["done"] = lesson["id"] in done
    return jsonify({"course": data})


@bp.get("/courses/<course_slug>/lessons/<lesson_slug>")
@jwt_required()
def get_lesson(course_slug, lesson_slug):
    lesson = (
        Lesson.query.join(Course)
        .filter(Course.slug == course_slug, Lesson.slug == lesson_slug)
        .first()
    )
    if lesson is None:
        return jsonify({"error": "Leçon introuvable."}), 404

    siblings = lesson.course.lessons
    index = [item.id for item in siblings].index(lesson.id)
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()

    return jsonify({
        "lesson": lesson.to_dict(with_blocks=True),
        "course": {
            "slug": lesson.course.slug,
            "title": lesson.course.title,
            "icon": lesson.course.icon,
            "position": lesson.course.position,
        },
        "done": progress is not None,
        "quiz_score": progress.quiz_score if progress else None,
        "prev": siblings[index - 1].slug if index > 0 else None,
        "next": siblings[index + 1].slug if index + 1 < len(siblings) else None,
    })


@bp.get("/courses/<course_slug>/exercises/<exercise_slug>")
@jwt_required()
def get_exercise(course_slug, exercise_slug):
    exercise = (
        Exercise.query.join(Course)
        .filter(Course.slug == course_slug, Exercise.slug == exercise_slug)
        .first()
    )
    if exercise is None:
        return jsonify({"error": "Exercice introuvable."}), 404
    return jsonify({
        "exercise": exercise.to_dict(detailed=True),
        "course": {
            "slug": exercise.course.slug,
            "title": exercise.course.title,
            "icon": exercise.course.icon,
            "position": exercise.course.position,
        },
    })
