"""Modèles SQLAlchemy : comptes, cours, leçons, exercices, progression, sécurité."""
import unicodedata
from datetime import UTC, datetime

from .extensions import db


def utcnow() -> datetime:
    """Heure UTC sans fuseau : c'est ce que stockent SQLite et PostgreSQL (TIMESTAMP)."""
    return datetime.now(UTC).replace(tzinfo=None)


def iso(moment: datetime | None) -> str | None:
    """Sérialise une date stockée en UTC, fuseau explicite (sinon le navigateur
    l'interprète comme une heure locale)."""
    return moment.replace(tzinfo=UTC).isoformat() if moment else None


def username_key(username: str) -> str:
    """Forme de comparaison d'un pseudo : « Élodie » et « élodie » sont le même compte."""
    return unicodedata.normalize("NFKC", username).casefold()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    username_key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    # Preuve de l'acceptation des conditions d'utilisation
    terms_accepted_at = db.Column(db.DateTime)
    terms_version = db.Column(db.String(20))

    # Incrémenté à chaque changement de mot de passe : invalide les sessions ouvertes.
    token_version = db.Column(db.Integer, default=0, server_default="0", nullable=False)

    progress = db.relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    submissions = db.relationship("Submission", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_admin": self.is_admin,
            "created_at": iso(self.created_at),
            "terms_version": self.terms_version,
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    summary = db.Column(db.Text, default="")
    category = db.Column(db.String(80), default="Autre")
    level = db.Column(db.String(40), default="débutant")
    icon = db.Column(db.String(16), default="")   # monogramme affiché (« Py », « SQL »…)
    position = db.Column(db.Integer, default=0)

    lessons = db.relationship(
        "Lesson", back_populates="course", cascade="all, delete-orphan",
        order_by="Lesson.position",
    )
    exercises = db.relationship(
        "Exercise", back_populates="course", cascade="all, delete-orphan",
        order_by="Exercise.position",
    )

    def to_dict(self, with_children=False):
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "summary": self.summary,
            "category": self.category,
            "level": self.level,
            "icon": self.icon,
            "position": self.position,
            "lessons_count": len(self.lessons),
            "exercises_count": len(self.exercises),
        }
        if with_children:
            data["lessons"] = [lesson.to_dict() for lesson in self.lessons]
            data["exercises"] = [exercise.to_dict() for exercise in self.exercises]
        return data


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    duration_min = db.Column(db.Integer, default=10)
    position = db.Column(db.Integer, default=0)
    # Contenu interactif : liste de blocs {type: video | text | code | callout | quiz, ...}
    blocks = db.Column(db.JSON, default=list)

    course = db.relationship("Course", back_populates="lessons")

    __table_args__ = (db.UniqueConstraint("course_id", "slug", name="uq_lesson_slug"),)

    @property
    def quizzes(self) -> list[dict]:
        return [block for block in (self.blocks or []) if block.get("type") == "quiz"]

    def to_dict(self, with_blocks=False):
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "duration_min": self.duration_min,
            "position": self.position,
            "course_slug": self.course.slug if self.course else None,
        }
        if with_blocks:
            data["blocks"] = [_public_block(block) for block in (self.blocks or [])]
        return data


def _public_block(block: dict) -> dict:
    """Retire les réponses des quiz avant envoi au navigateur."""
    if block.get("type") != "quiz":
        return block
    return {key: value for key, value in block.items() if key not in ("answer", "explanation")}


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    statement = db.Column(db.Text, default="")          # énoncé du TP (markdown)
    kind = db.Column(db.String(20), default="python")   # python | sql | quiz
    difficulty = db.Column(db.String(20), default="facile")
    starter_code = db.Column(db.Text, default="")
    solution = db.Column(db.Text, default="")
    hints = db.Column(db.JSON, default=list)
    # python -> {"tests": [...]} ; sql -> {"schema", "expected_query"} ; quiz -> {"questions"}
    spec = db.Column(db.JSON, default=dict)
    position = db.Column(db.Integer, default=0)

    course = db.relationship("Course", back_populates="exercises")
    submissions = db.relationship(
        "Submission", back_populates="exercise", cascade="all, delete-orphan"
    )

    __table_args__ = (db.UniqueConstraint("course_id", "slug", name="uq_exercise_slug"),)

    def to_dict(self, detailed=False):
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "kind": self.kind,
            "difficulty": self.difficulty,
            "position": self.position,
            "course_slug": self.course.slug if self.course else None,
        }
        if detailed:
            data.update({
                "statement": self.statement,
                "starter_code": self.starter_code,
                "hints": self.hints or [],
                "spec": _public_spec(self.kind, self.spec or {}),
            })
        return data


def _public_spec(kind: str, spec: dict) -> dict:
    """N'expose que ce dont le navigateur a besoin, jamais la solution attendue."""
    if kind == "sql":
        return {"schema": spec.get("schema", "")}
    if kind == "quiz":
        return {
            "questions": [
                {key: value for key, value in question.items()
                 if key not in ("answer", "explanation")}
                for question in spec.get("questions", [])
            ]
        }
    if kind == "python":
        return {"tests": [test.get("name") for test in spec.get("tests", [])]}
    return {}


class Progress(db.Model):
    """Une leçon terminée par un utilisateur."""
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)
    quiz_score = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    user = db.relationship("User", back_populates="progress")
    lesson = db.relationship("Lesson")

    __table_args__ = (db.UniqueConstraint("user_id", "lesson_id", name="uq_progress"),)


class Submission(db.Model):
    """Une tentative sur un exercice."""
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    code = db.Column(db.Text, default="")
    passed = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Float, default=0.0)
    output = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    user = db.relationship("User", back_populates="submissions")
    exercise = db.relationship("Exercise", back_populates="submissions")

    def to_dict(self):
        exercise = self.exercise
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "exercise_title": exercise.title if exercise else None,
            "exercise_slug": exercise.slug if exercise else None,
            "course_slug": exercise.course.slug if exercise else None,
            "passed": self.passed,
            "score": self.score,
            "created_at": iso(self.created_at),
        }


class RevokedToken(db.Model):
    """Session fermée avant son expiration (déconnexion). Purgée une fois expirée."""
    __tablename__ = "revoked_tokens"

    jti = db.Column(db.String(36), primary_key=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)


class Throttle(db.Model):
    """Compteur de tentatives, commun à tous les workers.

    La clé est une empreinte (HMAC) : ni adresse IP ni identifiant en clair.
    """
    __tablename__ = "throttles"

    key = db.Column(db.String(64), primary_key=True)
    hits = db.Column(db.Integer, default=0, nullable=False)
    window_start = db.Column(db.DateTime, default=utcnow, nullable=False)
    strikes = db.Column(db.Integer, default=0, nullable=False)
    blocked_until = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False, index=True)
