"""Les migrations doivent produire exactement le schéma décrit par les modèles."""
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from flask_migrate import upgrade

from app import create_app
from app.config import TestConfig
from app.extensions import db


def test_migrations_alignees_sur_les_modeles(tmp_path):
    class Fichier(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'schema.db'}"

    app = create_app(Fichier)
    with app.app_context():
        upgrade()
        with db.engine.connect() as connection:
            context = MigrationContext.configure(connection, opts={"compare_type": True})
            differences = compare_metadata(context, db.metadata)
        db.engine.dispose()
    assert differences == []


def test_base_de_la_premiere_version_migree_sans_perte(tmp_path):
    """Une base créée avant les migrations est reconnue, puis mise à niveau."""
    import sqlite3

    path = tmp_path / "ancienne.db"
    ancienne = sqlite3.connect(path)
    ancienne.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255) NOT NULL,
            username VARCHAR(80) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN NOT NULL, created_at DATETIME NOT NULL);
        CREATE UNIQUE INDEX ix_users_email ON users (email);
        CREATE TABLE courses (id INTEGER PRIMARY KEY, slug VARCHAR(80) NOT NULL,
            title VARCHAR(160) NOT NULL, summary TEXT, category VARCHAR(80),
            level VARCHAR(40), icon VARCHAR(16), position INTEGER);
        CREATE UNIQUE INDEX ix_courses_slug ON courses (slug);
        CREATE TABLE lessons (id INTEGER PRIMARY KEY, course_id INTEGER NOT NULL REFERENCES courses(id),
            slug VARCHAR(80) NOT NULL, title VARCHAR(160) NOT NULL, duration_min INTEGER,
            position INTEGER, blocks JSON, CONSTRAINT uq_lesson_slug UNIQUE (course_id, slug));
        CREATE TABLE exercises (id INTEGER PRIMARY KEY, course_id INTEGER NOT NULL REFERENCES courses(id),
            slug VARCHAR(80) NOT NULL, title VARCHAR(160) NOT NULL, statement TEXT, kind VARCHAR(20),
            difficulty VARCHAR(20), starter_code TEXT, solution TEXT, hints JSON, spec JSON,
            position INTEGER, CONSTRAINT uq_exercise_slug UNIQUE (course_id, slug));
        CREATE TABLE progress (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            lesson_id INTEGER NOT NULL REFERENCES lessons(id), quiz_score FLOAT,
            completed_at DATETIME NOT NULL, CONSTRAINT uq_progress UNIQUE (user_id, lesson_id));
        CREATE TABLE submissions (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            exercise_id INTEGER NOT NULL REFERENCES exercises(id), code TEXT, passed BOOLEAN NOT NULL,
            score FLOAT, output TEXT, created_at DATETIME NOT NULL);
        INSERT INTO users VALUES (1, 'a@test.fr', 'Alice', 'hash', 0, '2026-11-01 10:00:00');
        INSERT INTO users VALUES (2, 'b@test.fr', 'alice', 'hash', 0, '2026-11-02 10:00:00');
    """)
    ancienne.commit()
    ancienne.close()

    class Ancienne(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{path}"

    app = create_app(Ancienne)
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0, result.output
    assert "Base existante reconnue" in result.output

    with app.app_context():
        from app.models import User

        keys = {user.username: user.username_key for user in User.query.order_by(User.id)}
        db.engine.dispose()
    # Les deux comptes sont conservés ; le plus ancien garde la clé « alice ».
    assert keys == {"Alice": "alice", "alice": "alice#2"}
