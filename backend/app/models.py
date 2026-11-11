"""Modeles SQLAlchemy : utilisateurs, cours, lecons, exercices, progression."""
from datetime import UTC, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def _now():
    return datetime.now(UTC)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    progress = db.relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    submissions = db.relationship("Submission", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    summary = db.Column(db.Text, default="")
    category = db.Column(db.String(80), default="Autre")
    level = db.Column(db.String(40), default="debutant")
    icon = db.Column(db.String(16), default="📘")
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
            data["exercises"] = [ex.to_dict() for ex in self.exercises]
        return data


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    duration_min = db.Column(db.Integer, default=10)
    position = db.Column(db.Integer, default=0)
    # Contenu interactif : liste de blocs {type: text|code|callout|quiz, ...}
    blocks = db.Column(db.JSON, default=list)

    course = db.relationship("Course", back_populates="lessons")

    __table_args__ = (db.UniqueConstraint("course_id", "slug", name="uq_lesson_slug"),)

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
            data["blocks"] = [_public_block(b) for b in (self.blocks or [])]
        return data


def _public_block(block: dict) -> dict:
    """Retire les reponses des quiz avant envoi au client."""
    if block.get("type") != "quiz":
        return block
    clean = {k: v for k, v in block.items() if k not in ("answer", "explanation")}
    return clean


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    statement = db.Column(db.Text, default="")       # enonce du TP (markdown)
    kind = db.Column(db.String(20), default="python")  # python | sql | quiz
    difficulty = db.Column(db.String(20), default="facile")
    starter_code = db.Column(db.Text, default="")
    solution = db.Column(db.Text, default="")
    hints = db.Column(db.JSON, default=list)
    # python -> [{"name","code"}] ; sql -> {"schema","expected_query"} ; quiz -> {"questions":[...]}
    spec = db.Column(db.JSON, default=dict)
    position = db.Column(db.Integer, default=0)

    course = db.relationship("Course", back_populates="exercises")
    submissions = db.relationship("Submission", back_populates="exercise", cascade="all, delete-orphan")

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
            data.update(
                {
                    "statement": self.statement,
                    "starter_code": self.starter_code,
                    "hints": self.hints or [],
                    "spec": _public_spec(self.kind, self.spec or {}),
                }
            )
        return data


def _public_spec(kind: str, spec: dict) -> dict:
    """N'expose que ce dont le client a besoin (jamais la solution attendue)."""
    if kind == "sql":
        return {"schema": spec.get("schema", ""), "question": spec.get("question", "")}
    if kind == "quiz":
        return {
            "questions": [
                {k: v for k, v in q.items() if k not in ("answer", "explanation")}
                for q in spec.get("questions", [])
            ]
        }
    if kind == "python":
        return {"tests": [t.get("name") for t in spec.get("tests", [])]}
    return {}


class Progress(db.Model):
    """Une lecon terminee par un utilisateur."""
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)
    quiz_score = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=_now, nullable=False)

    user = db.relationship("User", back_populates="progress")
    lesson = db.relationship("Lesson")

    __table_args__ = (db.UniqueConstraint("user_id", "lesson_id", name="uq_progress"),)


class Submission(db.Model):
    """Une tentative sur un exercice / TP."""
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    code = db.Column(db.Text, default="")
    passed = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Float, default=0.0)
    output = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    user = db.relationship("User", back_populates="submissions")
    exercise = db.relationship("Exercise", back_populates="submissions")

    def to_dict(self):
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "exercise_title": self.exercise.title if self.exercise else None,
            "course_slug": self.exercise.course.slug if self.exercise else None,
            "passed": self.passed,
            "score": self.score,
            "created_at": self.created_at.isoformat(),
        }
