"""Commandes `flask ...` : initialisation de la base et chargement du contenu."""
import click
from flask import Flask

from .extensions import db


def register(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Cree les tables."""
        from . import models  # noqa: F401

        db.create_all()
        click.echo("Tables creees.")

    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Supprime le contenu avant de recharger.")
    def seed(reset):
        """Charge les cours, lecons et exercices."""
        from .seed import load

        counts = load(reset=reset)
        click.echo(
            f"{counts['courses']} cours, {counts['lessons']} lecons, "
            f"{counts['exercises']} exercices charges."
        )

    @app.cli.command("create-user")
    @click.argument("email")
    @click.argument("username")
    @click.argument("password")
    @click.option("--admin", is_flag=True)
    def create_user(email, username, password, admin):
        """Cree un compte depuis la ligne de commande."""
        from .models import User

        user = User(email=email.lower(), username=username, is_admin=admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Utilisateur {username} cree (id={user.id}).")
