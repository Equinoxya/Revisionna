"""Chargement du catalogue de cours. Peut être rejoué sans risque."""
from ..extensions import db
from ..models import Course, Exercise, Lesson
from . import (
    c_aiops,
    c_cicd,
    c_deploy,
    c_devops,
    c_django,
    c_docker,
    c_flask,
    c_ml,
    c_nosql,
    c_python,
    c_react,
    c_reseau,
    c_sql,
    c_systeme,
)

CATALOG = [
    c_python.COURSE,
    c_flask.COURSE,
    c_django.COURSE,
    c_react.COURSE,
    c_sql.COURSE,
    c_nosql.COURSE,
    c_ml.COURSE,
    c_aiops.COURSE,
    c_systeme.COURSE,
    c_reseau.COURSE,
    c_devops.COURSE,
    c_docker.COURSE,
    c_cicd.COURSE,
    c_deploy.COURSE,
]


def _blocs(lesson_spec: dict) -> list[dict]:
    """Blocs d'une leçon, précédés de l'emplacement de sa vidéo explicative.

    Tant que la leçon n'a pas de clé "video" (une URL), le lecteur affiche « à venir ».
    """
    video = {"type": "video", "url": lesson_spec.get("video", "")}
    return [video, *lesson_spec.get("blocks", [])]


def load(reset: bool = False) -> dict:
    """Insère ou met à jour les cours du catalogue. Ne touche ni aux comptes ni à la progression."""
    db.create_all()

    if reset:
        Exercise.query.delete()
        Lesson.query.delete()
        Course.query.delete()
        db.session.commit()

    counts = {"courses": 0, "lessons": 0, "exercises": 0}

    for position, spec in enumerate(CATALOG):
        course = Course.query.filter_by(slug=spec["slug"]).first()
        if course is None:
            course = Course(slug=spec["slug"])
            db.session.add(course)
        course.title = spec["title"]
        course.summary = spec.get("summary", "")
        course.category = spec.get("category", "Autre")
        course.level = spec.get("level", "débutant")
        course.icon = spec.get("icon", "")
        course.position = position
        db.session.flush()
        counts["courses"] += 1

        for index, lesson_spec in enumerate(spec.get("lessons", [])):
            lesson = Lesson.query.filter_by(
                course_id=course.id, slug=lesson_spec["slug"]
            ).first()
            if lesson is None:
                lesson = Lesson(course_id=course.id, slug=lesson_spec["slug"])
                db.session.add(lesson)
            lesson.title = lesson_spec["title"]
            lesson.duration_min = lesson_spec.get("duration_min", 10)
            lesson.blocks = _blocs(lesson_spec)
            lesson.position = index
            counts["lessons"] += 1

        for index, ex_spec in enumerate(spec.get("exercises", [])):
            exercise = Exercise.query.filter_by(
                course_id=course.id, slug=ex_spec["slug"]
            ).first()
            if exercise is None:
                exercise = Exercise(course_id=course.id, slug=ex_spec["slug"])
                db.session.add(exercise)
            exercise.title = ex_spec["title"]
            exercise.statement = ex_spec.get("statement", "")
            exercise.kind = ex_spec.get("kind", "python")
            exercise.difficulty = ex_spec.get("difficulty", "facile")
            exercise.starter_code = ex_spec.get("starter_code", "")
            exercise.solution = ex_spec.get("solution", "")
            exercise.hints = ex_spec.get("hints", [])
            exercise.spec = ex_spec.get("spec", {})
            exercise.position = index
            counts["exercises"] += 1

    db.session.commit()
    return counts
