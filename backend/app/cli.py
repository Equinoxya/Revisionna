"""Commandes `flask ...` : base de données, contenu, comptes, ménage."""
from datetime import timedelta

import click
from flask import Flask, current_app
from flask_migrate import stamp, upgrade
from sqlalchemy import inspect

from .extensions import db

BASELINE = "0001"   # schéma de la première version, créé à l'époque sans migrations


def register(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Crée ou met à jour le schéma (migrations Alembic)."""
        tables = set(inspect(db.engine).get_table_names())
        if "users" in tables and "alembic_version" not in tables:
            # Base créée par la toute première version : on la marque comme telle,
            # puis les migrations suivantes s'appliquent sans perdre de données.
            stamp(revision=BASELINE)
            click.echo("Base existante reconnue (schéma initial).")
        upgrade()
        click.echo("Schéma à jour.")

    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Supprime le contenu avant de le recharger.")
    def seed(reset):
        """Charge les cours, leçons et exercices."""
        from .seed import load

        counts = load(reset=reset)
        click.echo(
            f"{counts['courses']} cours, {counts['lessons']} leçons, "
            f"{counts['exercises']} exercices chargés."
        )

    password_option = click.option(
        "--password", prompt="Mot de passe", hide_input=True, confirmation_prompt=True,
        envvar="NEW_PASSWORD", help="Demandé au clavier (jamais en argument : il "
        "resterait dans l'historique du terminal).",
    )

    @app.cli.command("create-user")
    @click.argument("email")
    @click.argument("username")
    @password_option
    @click.option("--admin", is_flag=True)
    def create_user(email, username, password, admin):
        """Crée un compte depuis la ligne de commande."""
        from .api.auth import email_error, username_error
        from .models import User, username_key, utcnow
        from .services import passwords

        email = email.strip().lower()
        problems = [email_error(email), username_error(username)]
        problems += passwords.problems(password, email=email, username=username)
        problems = [problem for problem in problems if problem]
        if problems:
            raise click.ClickException(" ".join(problems))

        user = User(
            email=email, username=username, username_key=username_key(username),
            password_hash=passwords.hash_password(password), is_admin=admin,
            terms_accepted_at=utcnow(), terms_version=current_app.config["TERMS_VERSION"],
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"Compte {username} créé (id={user.id}).")

    @app.cli.command("set-password")
    @click.argument("identifier")
    @password_option
    def set_password(identifier, password):
        """Réinitialise le mot de passe d'un compte (email ou nom d'utilisateur)."""
        from .api.auth import find_user
        from .services import passwords, throttle

        user = find_user(identifier.strip())
        if user is None:
            raise click.ClickException("Compte introuvable.")
        problems = passwords.problems(password, email=user.email, username=user.username)
        if problems:
            raise click.ClickException(" ".join(problems))

        user.password_hash = passwords.hash_password(password)
        user.token_version += 1          # ferme les sessions ouvertes
        db.session.commit()
        throttle.unlock(identifier.strip().casefold())
        click.echo(f"Mot de passe de {user.username} modifié, sessions fermées.")

    @app.cli.command("unlock")
    @click.argument("identifier")
    def unlock(identifier):
        """Lève le blocage de connexion d'un identifiant (après trop d'échecs)."""
        from .services import throttle

        done = throttle.unlock(identifier.strip().casefold())
        click.echo("Blocage levé." if done else "Aucun blocage pour cet identifiant.")

    @app.cli.command("purge")
    @click.option("--inactive-months", type=int, default=None,
                  help="Supprime aussi les comptes inactifs depuis N mois "
                       "(défaut : INACTIVE_ACCOUNT_MONTHS).")
    @click.option("--dry-run", is_flag=True, help="Montre ce qui serait supprimé.")
    def purge(inactive_months, dry_run):
        """Applique les durées de conservation : jetons expirés, compteurs, comptes inactifs."""
        from sqlalchemy import func

        from .models import User, utcnow
        from .services import activity, throttle

        months = inactive_months or current_app.config["INACTIVE_ACCOUNT_MONTHS"]
        limit = utcnow() - timedelta(days=30 * months)
        last_seen = func.coalesce(User.last_login_at, User.created_at)
        inactive = User.query.filter(last_seen < limit, User.is_admin.is_(False)).all()

        if dry_run:
            click.echo(f"{len(inactive)} compte(s) inactif(s) depuis plus de {months} mois.")
            return

        cleaned = throttle.purge()
        for user in inactive:
            activity.delete_user(user.id)
            db.session.delete(user)
        db.session.commit()
        click.echo(
            f"{cleaned['revoked_tokens']} jeton(s) expiré(s), {cleaned['throttles']} compteur(s), "
            f"{len(inactive)} compte(s) inactif(s) supprimé(s)."
        )
