"""Limitation des tentatives, stockée en base.

Pourquoi la base plutôt que la mémoire : avec plusieurs workers, un compteur en
mémoire est propre à chaque processus (un attaquant aurait autant d'essais que
de workers) et disparaît au redémarrage.

Deux mécanismes :

- un compteur à fenêtre fixe (`hit`, `wait_time`) pour limiter un débit ;
- une temporisation par compte pour la connexion : après 5 échecs, l'attente
  double à chaque nouvel échec (1 min, 2, 4… plafonnée à 15 min), avec au plus
  25 échecs par 24 heures. Ce sont les ordres de grandeur de la recommandation
  de la CNIL sur les mots de passe.

Les clés sont des empreintes HMAC : la table ne contient ni adresse IP ni
identifiant en clair.
"""
from __future__ import annotations

import hashlib
import hmac
import math
from datetime import timedelta

from flask import current_app
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import RevokedToken, Throttle, utcnow

FREE_FAILURES = 5
BASE_DELAY = 60          # secondes d'attente après le 5e échec
MAX_DELAY = 15 * 60
DAILY_FAILURES = 25
DAY = timedelta(hours=24)


def _key(scope: str, subject: str) -> str:
    secret = current_app.config["SECRET_KEY"].encode()
    return hmac.new(secret, f"{scope}|{subject}".encode(), hashlib.sha256).hexdigest()


def _locked(key: str) -> Throttle:
    """Ligne du compteur, verrouillée le temps de la transaction (créée au besoin)."""
    row = db.session.get(Throttle, key, with_for_update=True)
    if row is None:
        row = Throttle(key=key, hits=0, strikes=0, window_start=utcnow())
        db.session.add(row)
        try:
            db.session.flush()
        except IntegrityError:  # créée entre-temps par un autre worker
            db.session.rollback()
            row = db.session.get(Throttle, key, with_for_update=True)
    return row


def _seconds_until(moment) -> int:
    return max(1, math.ceil((moment - utcnow()).total_seconds()))


# --- Compteur à fenêtre fixe ------------------------------------------------

def wait_time(scope: str, subject, *, limit: int, window: timedelta) -> int | None:
    """Secondes à attendre si la limite est atteinte, sinon None. Ne compte rien."""
    row = db.session.get(Throttle, _key(scope, str(subject)))
    if row is None or utcnow() - row.window_start >= window or row.hits < limit:
        return None
    return _seconds_until(row.window_start + window)


def hit(scope: str, subject, *, limit: int, window: timedelta) -> int | None:
    """Compte un passage. Renvoie None s'il est autorisé, sinon l'attente en secondes."""
    row = _locked(_key(scope, str(subject)))
    now = utcnow()
    if now - row.window_start >= window:
        row.hits, row.window_start = 0, now

    if row.hits >= limit:
        wait = _seconds_until(row.window_start + window)
        db.session.commit()
        return wait

    row.hits += 1
    row.updated_at = now
    db.session.commit()
    return None


# --- Temporisation de connexion par compte -----------------------------------

def login_wait(identifier: str) -> int | None:
    """Attente imposée avant un nouvel essai sur cet identifiant, ou None."""
    row = db.session.get(Throttle, _key("login", identifier))
    if row is None or row.blocked_until is None or row.blocked_until <= utcnow():
        return None
    return _seconds_until(row.blocked_until)


def login_failed(identifier: str) -> None:
    row = _locked(_key("login", identifier))
    now = utcnow()
    if now - row.window_start >= DAY:
        row.hits, row.strikes, row.window_start = 0, 0, now

    row.hits += 1
    row.strikes += 1
    if row.hits >= DAILY_FAILURES:
        row.blocked_until = row.window_start + DAY
    elif row.strikes >= FREE_FAILURES:
        delay = min(BASE_DELAY * 2 ** (row.strikes - FREE_FAILURES), MAX_DELAY)
        row.blocked_until = now + timedelta(seconds=delay)
    row.updated_at = now
    db.session.commit()


def login_succeeded(identifier: str) -> None:
    row = db.session.get(Throttle, _key("login", identifier))
    if row is not None and (row.strikes or row.blocked_until):
        row.strikes, row.blocked_until = 0, None
        db.session.commit()


def unlock(identifier: str) -> bool:
    """Lève un blocage (commande d'administration)."""
    row = db.session.get(Throttle, _key("login", identifier))
    if row is None:
        return False
    db.session.delete(row)
    db.session.commit()
    return True


# --- Ménage ---------------------------------------------------------------

def purge() -> dict:
    """Supprime les compteurs inactifs depuis plus d'un jour et les jetons expirés."""
    now = utcnow()
    throttles = Throttle.query.filter(
        Throttle.updated_at < now - DAY - timedelta(hours=1)
    ).delete(synchronize_session=False)
    tokens = RevokedToken.query.filter(RevokedToken.expires_at < now).delete(
        synchronize_session=False
    )
    db.session.commit()
    return {"throttles": throttles, "revoked_tokens": tokens}


def human(seconds: int) -> str:
    """« 45 secondes », « 3 minutes », « 2 heures »."""
    if seconds < 60:
        return f"{seconds} seconde{'s' if seconds > 1 else ''}"
    minutes = math.ceil(seconds / 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    hours = math.ceil(minutes / 60)
    return f"{hours} heure{'s' if hours > 1 else ''}"
