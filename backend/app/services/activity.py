"""Journal d'activite en NoSQL (MongoDB) - degrade proprement si absent.

Illustration du cours NoSQL : documents libres, pas de schema, ecriture
best-effort qui ne doit jamais casser la requete HTTP.
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
        except Exception:  # noqa: BLE001
            current_app.logger.warning("MongoDB injoignable, journal desactive")
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
        current_app.logger.warning("Echec ecriture journal NoSQL")


def recent(user_id: int, limit: int = 20) -> list[dict]:
    collection = _collection()
    if collection is None:
        return []
    try:
        cursor = collection.find({"user_id": user_id}).sort("at", -1).limit(limit)
        return [
            {k: (v.isoformat() if isinstance(v, datetime) else v)
             for k, v in doc.items() if k != "_id"}
            for doc in cursor
        ]
    except Exception:  # noqa: BLE001
        return []
