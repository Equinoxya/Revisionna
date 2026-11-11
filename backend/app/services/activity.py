"""Journal d'activité en NoSQL (MongoDB), optionnel.

Illustration du cours NoSQL : documents libres, pas de schéma. L'écriture est
« au mieux » : une base de journalisation en panne ne doit jamais faire échouer
une requête.

Données personnelles : chaque document porte l'identifiant du compte. Ils sont
donc inclus dans l'export, supprimés avec le compte, et effacés automatiquement
après `ACTIVITY_RETENTION_DAYS` jours (index TTL).
"""
from __future__ import annotations

from datetime import UTC, datetime

from flask import current_app

_client = None
_checked = False


def _collection():
    global _client, _checked
    url = current_app.config.get("MONGO_URL")
    if not url:
        return None
    if not _checked:
        _checked = True
        try:
            from pymongo import MongoClient

            _client = MongoClient(url, serverSelectionTimeoutMS=800)
            _client.admin.command("ping")
            days = current_app.config["ACTIVITY_RETENTION_DAYS"]
            _client[current_app.config["MONGO_DB"]]["activity"].create_index(
                "at", expireAfterSeconds=days * 86400, name="expiration"
            )
        except Exception:  # noqa: BLE001
            current_app.logger.warning("MongoDB injoignable ou index refusé : journal désactivé")
            _client = None
    if _client is None:
        return None
    return _client[current_app.config["MONGO_DB"]]["activity"]


def log(event: str, user_id: int | None = None, **payload) -> None:
    collection = _collection()
    if collection is None:
        return
    try:
        collection.insert_one({
            "event": event,
            "user_id": user_id,
            "at": datetime.now(UTC),
            **payload,
        })
    except Exception:  # noqa: BLE001
        current_app.logger.warning("échec d'écriture dans le journal d'activité")


def _plain(document: dict) -> dict:
    return {
        key: (value.isoformat() if isinstance(value, datetime) else value)
        for key, value in document.items()
        if key not in ("_id", "user_id")
    }


def export(user_id: int, limit: int = 5000) -> list[dict]:
    """Tous les événements d'un compte, du plus ancien au plus récent."""
    collection = _collection()
    if collection is None:
        return []
    try:
        cursor = collection.find({"user_id": user_id}).sort("at", 1).limit(limit)
        return [_plain(document) for document in cursor]
    except Exception:  # noqa: BLE001
        current_app.logger.warning("échec de lecture du journal d'activité")
        return []


def delete_user(user_id: int) -> int:
    """Efface le journal d'un compte supprimé. Renvoie le nombre de documents."""
    collection = _collection()
    if collection is None:
        return 0
    try:
        return collection.delete_many({"user_id": user_id}).deleted_count
    except Exception:  # noqa: BLE001
        # À ne pas laisser passer en silence : la suppression doit être complète.
        current_app.logger.error("journal d'activité NON effacé pour le compte %s", user_id)
        return 0
