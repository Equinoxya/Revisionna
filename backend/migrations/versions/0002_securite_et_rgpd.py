"""Sécurité des sessions et droits RGPD.

- `users` : clé de comparaison du pseudo (connexion insensible à la casse),
  dernière connexion (purge des comptes inactifs), preuve d'acceptation des
  conditions d'utilisation, version de session (fermeture des sessions au
  changement de mot de passe) ;
- `revoked_tokens` : sessions fermées par une déconnexion ;
- `throttles` : compteurs de tentatives communs à tous les workers.

Revision ID: 0002
Revises: 0001
"""
import unicodedata

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "revoked_tokens",
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("jti"),
    )
    with op.batch_alter_table("revoked_tokens", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_revoked_tokens_expires_at"), ["expires_at"], unique=False)

    op.create_table(
        "throttles",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column("strikes", sa.Integer(), nullable=False),
        sa.Column("blocked_until", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    with op.batch_alter_table("throttles", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_throttles_updated_at"), ["updated_at"], unique=False)

    # 1. Nouvelles colonnes. `username_key` reste facultative le temps de la remplir.
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("username_key", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("last_login_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("terms_accepted_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("terms_version", sa.String(length=20), nullable=True))
        batch_op.add_column(
            sa.Column("token_version", sa.Integer(), server_default="0", nullable=False)
        )

    # 2. Remplissage pour les comptes existants.
    users = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("username", sa.String),
        sa.column("username_key", sa.String),
    )
    bind = op.get_bind()
    seen = set()
    rows = bind.execute(sa.select(users.c.id, users.c.username).order_by(users.c.id)).fetchall()
    for user_id, username in rows:
        key = unicodedata.normalize("NFKC", username).casefold()
        if key in seen:
            # Deux pseudos ne différant que par la casse : le plus ancien garde la
            # clé ; l'autre se connectera avec son email.
            key = f"{key[:60]}#{user_id}"
        seen.add(key)
        bind.execute(users.update().where(users.c.id == user_id).values(username_key=key))

    # 3. La colonne devient obligatoire et unique.
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("username_key", existing_type=sa.String(length=80), nullable=False)
        batch_op.create_index(batch_op.f("ix_users_username_key"), ["username_key"], unique=True)


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_username_key"))
        batch_op.drop_column("token_version")
        batch_op.drop_column("terms_version")
        batch_op.drop_column("terms_accepted_at")
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("username_key")

    with op.batch_alter_table("throttles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_throttles_updated_at"))
    op.drop_table("throttles")

    with op.batch_alter_table("revoked_tokens", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_revoked_tokens_expires_at"))
    op.drop_table("revoked_tokens")
