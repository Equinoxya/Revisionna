"""Assistant IA : Ollama (local) ou OpenAI, avec repli hors-ligne.

Le but pedagogique est de montrer qu'on peut brancher le meme prompt
sur un modele local ou une API distante derriere la meme interface.
"""
from __future__ import annotations

import requests
from flask import current_app

SYSTEM_PROMPT = (
    "Tu es un tuteur de programmation bienveillant. "
    "Tu reponds en francais, en 4 phrases maximum. "
    "Tu donnes un INDICE, jamais la solution complete ni le code final."
)

TIMEOUT = 30


class AIUnavailable(RuntimeError):
    pass


def provider() -> str:
    return (current_app.config.get("AI_PROVIDER") or "").lower()


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
        resp = requests.post(
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
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise AIUnavailable(f"Ollama injoignable : {exc}") from exc


def _openai(prompt: str, system: str) -> str:
    key = current_app.config["OPENAI_API_KEY"]
    if not key:
        raise AIUnavailable("OPENAI_API_KEY absente")
    try:
        resp = requests.post(
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
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise AIUnavailable(f"OpenAI injoignable : {exc}") from exc


def _offline(prompt: str) -> str:
    """Repli sans modele : heuristique simple pour que l'app reste utilisable."""
    low = prompt.lower()
    if "traceback" in low or "error" in low or "erreur" in low:
        return (
            "Lis la derniere ligne du traceback : elle nomme le type d'erreur et la ligne. "
            "Verifie les noms de variables et les types manipules. "
            "(Aucun fournisseur IA configure : voir AI_PROVIDER dans .env)"
        )
    if "sql" in low:
        return (
            "Pense a l'ordre SELECT / FROM / JOIN / WHERE / GROUP BY / HAVING / ORDER BY, "
            "et verifie la cle de jointure. "
            "(Aucun fournisseur IA configure : voir AI_PROVIDER dans .env)"
        )
    return (
        "Decoupe le probleme : quelles entrees, quelle sortie attendue, quelle etape bloque ? "
        "Ecris d'abord un cas simple a la main. "
        "(Aucun fournisseur IA configure : voir AI_PROVIDER dans .env)"
    )


def hint_prompt(exercise, code: str, output: str) -> str:
    return (
        f"Exercice : {exercise.title}\n"
        f"Enonce :\n{exercise.statement[:1200]}\n\n"
        f"Code de l'eleve :\n```\n{code[:2000]}\n```\n\n"
        f"Resultat des tests :\n{output[:1200]}\n\n"
        "Donne un seul indice cible pour debloquer l'eleve."
    )
