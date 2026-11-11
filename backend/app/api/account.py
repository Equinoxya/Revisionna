"""Mon compte : rectification, export et suppression des données (droits RGPD)."""
from __future__ import annotations

import json
from datetime import timedelta

from flask import Blueprint, Response, jsonify
from flask_jwt_extended import current_user, jwt_required

from ..extensions import db
from ..models import Exercise, Lesson, Progress, Submission, User, iso, username_key, utcnow
from ..services import activity, sessions, throttle
from .auth import confirm_password, email_error, username_error
from .common import body, secret, text, too_many

bp = Blueprint("account", __name__, url_prefix="/api/me")

EXPORTS_PER_HOUR = 10


@bp.patch("")
@jwt_required()
def update_profile():
    """Droit de rectification : changer d'email ou de nom d'utilisateur."""
    data = body()
    refused = confirm_password(current_user, secret(data, "current_password"))
    if refused:
        return refused

    email = text(data, "email").lower() or current_user.email
    username = text(data, "username") or current_user.username

    errors = {}
    if problem := email_error(email):
        errors["email"] = problem
    if problem := username_error(username):
        errors["username"] = problem
    if errors:
        return jsonify({"errors": errors}), 400

    others = User.query.filter(User.id != current_user.id)
    conflicts = {}
    if others.filter_by(email=email).first():
        conflicts["email"] = "Un compte existe déjà avec cette adresse."
    if others.filter_by(username_key=username_key(username)).first():
        conflicts["username"] = "Ce nom d'utilisateur est déjà pris."
    if conflicts:
        return jsonify({"errors": conflicts}), 409

    current_user.email = email
    current_user.username = username
    current_user.username_key = username_key(username)
    db.session.commit()

    activity.log("profile_updated", current_user.id)
    return jsonify({"user": current_user.to_dict()})


@bp.get("/export")
@jwt_required()
def export_data():
    """Droits d'accès et de portabilité : toutes mes données, dans un format ouvert."""
    wait = throttle.hit(
        "export", current_user.id, limit=EXPORTS_PER_HOUR, window=timedelta(hours=1)
    )
    if wait:
        return too_many(wait)

    user = current_user
    lessons = (
        db.session.query(Progress, Lesson)
        .join(Lesson, Progress.lesson_id == Lesson.id)
        .filter(Progress.user_id == user.id)
        .order_by(Progress.completed_at)
        .all()
    )
    submissions = (
        db.session.query(Submission, Exercise)
        .join(Exercise, Submission.exercise_id == Exercise.id)
        .filter(Submission.user_id == user.id)
        .order_by(Submission.created_at)
        .all()
    )

    document = {
        "export": {"format": "revisionna-export-v1", "genere_le": iso(utcnow())},
        "compte": {
            "email": user.email,
            "nom_utilisateur": user.username,
            "cree_le": iso(user.created_at),
            "derniere_connexion": iso(user.last_login_at),
            "conditions_acceptees_le": iso(user.terms_accepted_at),
            "version_des_conditions": user.terms_version,
        },
        "lecons_terminees": [
            {
                "cours": lesson.course.slug,
                "lecon": lesson.slug,
                "titre": lesson.title,
                "score_quiz": progress.quiz_score,
                "terminee_le": iso(progress.completed_at),
            }
            for progress, lesson in lessons
        ],
        "soumissions": [
            {
                "cours": exercise.course.slug,
                "exercice": exercise.slug,
                "titre": exercise.title,
                "reussi": submission.passed,
                "score": submission.score,
                "reponse": submission.code,
                "retour_du_correcteur": submission.output,
                "soumis_le": iso(submission.created_at),
            }
            for submission, exercise in submissions
        ],
        "journal_activite": activity.export(user.id),
    }

    activity.log("data_exported", user.id)
    return Response(
        json.dumps(document, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": 'attachment; filename="revisionna-mes-donnees.json"'},
    )


@bp.delete("")
@jwt_required()
def delete_account():
    """Droit à l'effacement : supprime le compte et tout ce qui s'y rattache."""
    refused = confirm_password(current_user, secret(body(), "password"))
    if refused:
        return refused

    user_id = current_user.id
    activity.delete_user(user_id)
    sessions.revoke_current()
    db.session.delete(current_user)     # emporte progression et soumissions (cascade)
    db.session.commit()

    return sessions.close_session({"message": "Compte et données supprimés."})
