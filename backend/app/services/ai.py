"""Tuteur IA : Ollama (local) ou OpenAI (distant), avec repli hors ligne.

Le même prompt part vers un modèle local ou une API distante derrière une seule
interface. Ce qui est transmis : le titre et l'énoncé de l'exercice, le code de
l'élève et le retour des tests. Jamais son email ni son nom d'utilisateur.

Avec OpenAI, ces éléments quittent le serveur (et l'Union européenne) :
l'interface en avertit l'élève avant l'envoi (voir /api/meta, `ai_external`).
"""
from __future__ import annotations

import requests
from flask import current_app

SYSTEM_PROMPT = (
    "Tu es un tuteur de programmation bienveillant. "
    "Tu réponds en français, en 4 phrases maximum. "
    "Tu donnes un INDICE, jamais la solution complète ni le code final."
)

TIMEOUT = 30


class AIUnavailable(RuntimeError):
    pass


def provider() -> str:
    return (current_app.config.get("AI_PROVIDER") or "").strip().lower()


def ask(prompt: str, system: str = SYSTEM_PROMPT) -> dict:
    name = provider()
    if name == "ollama":
        return {"provider": "ollama", "answer": _ollama(prompt, system)}
    if name == "openai":
        return {"provider": "openai", "answer": _openai(prompt, system)}
    return {"provider": "offline", "answer": _offline(prompt)}


def _ollama(prompt: str, system: str) -> str:
    url = current_app.config["OLLAMA_URL"].rstrip("/") + "/api/chat"
    try:
        response = requests.post(
            url,
            json={
                "model": current_app.config["OLLAMA_MODEL"],
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise AIUnavailable("Ollama injoignable") from exc


def _openai(prompt: str, system: str) -> str:
    key = current_app.config["OPENAI_API_KEY"]
    if not key:
        raise AIUnavailable("OPENAI_API_KEY absente")
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": current_app.config["OPENAI_MODEL"],
                "temperature": 0.3,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, ValueError) as exc:
        # Le message d'origine peut contenir l'URL ou des en-têtes : on ne le relaie pas.
        raise AIUnavailable("OpenAI injoignable") from exc


def _offline(prompt: str) -> str:
    """Repli sans modèle : une heuristique simple, pour que l'application reste utilisable."""
    low = prompt.lower()
    if "traceback" in low or "error" in low or "erreur" in low:
        return (
            "Lisez la dernière ligne du message d'erreur : elle nomme le type d'erreur "
            "et la ligne en cause. Vérifiez les noms de variables et les types manipulés."
        )
    if "sql" in low or "select" in low:
        return (
            "Reprenez l'ordre SELECT / FROM / JOIN / WHERE / GROUP BY / HAVING / ORDER BY, "
            "et vérifiez la clé de jointure."
        )
    return (
        "Découpez le problème : quelles entrées, quelle sortie attendue, quelle étape bloque ? "
        "Écrivez d'abord un cas simple à la main."
    )


def hint_prompt(exercise, code: str, output: str) -> str:
    return (
        f"Exercice : {exercise.title}\n"
        f"Énoncé :\n{exercise.statement[:1200]}\n\n"
        f"Code de l'élève :\n```\n{code[:2000]}\n```\n\n"
        f"Résultat des tests :\n{output[:1200]}\n\n"
        "Donne un seul indice ciblé pour débloquer l'élève."
    )
