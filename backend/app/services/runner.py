"""Correction des exercices : Python, SQL, quiz.

Le code et les requêtes des élèves ne s'exécutent jamais dans le processus de
l'API. Selon la configuration :

- `RUNNER_SOCKET` défini : le travail part vers le service isolé (production) ;
- sinon, si `ALLOW_LOCAL_RUNNER` : sous-processus local limité (développement,
  tests) ;
- sinon : la correction est refusée, plutôt qu'exécutée sans isolation.
"""
from __future__ import annotations

from flask import current_app

from sandbox import client, core

MAX_CODE_CHARS = 20_000

_UNAVAILABLE = "Le service de correction est momentanément indisponible. Réessayez dans un instant."
_DISABLED = (
    "La correction automatique est désactivée sur ce serveur : aucun service "
    "d'exécution isolé n'est configuré."
)


def _refused(message: str) -> dict:
    return {"passed": False, "score": 0.0, "results": [], "output": message}


def _dispatch(job: dict) -> dict:
    socket_path = current_app.config.get("RUNNER_SOCKET")
    timeout = current_app.config["RUNNER_TIMEOUT"]

    if socket_path:
        try:
            return client.run(socket_path, job, timeout=timeout + 30)
        except client.RunnerUnavailable as exc:
            current_app.logger.error("service de correction injoignable : %s", exc)
            return _refused(_UNAVAILABLE)

    if not current_app.config.get("ALLOW_LOCAL_RUNNER"):
        current_app.logger.error("correction refusée : aucun exécuteur isolé configuré")
        return _refused(_DISABLED)

    if job["kind"] == "sql":
        return core.run_sql(job["query"], job["spec"], timeout=timeout)
    return core.run_python(job["code"], job["tests"], timeout=timeout)


def run_python(code: str, tests: list[dict]) -> dict:
    return _dispatch({"kind": "python", "code": code, "tests": tests})


def run_sql(query: str, spec: dict) -> dict:
    return _dispatch({
        "kind": "sql",
        "query": query,
        "spec": {
            "schema": spec.get("schema", ""),
            "expected_query": spec.get("expected_query", ""),
            "ordered": bool(spec.get("ordered", False)),
        },
    })


def run_quiz(answers: dict, spec: dict) -> dict:
    """`answers` = {identifiant de question: réponse choisie}."""
    questions = spec.get("questions", [])
    details, ok = [], 0
    for question in questions:
        qid = str(question.get("id"))
        correct = answers.get(qid) == question.get("answer")
        ok += int(correct)
        details.append({
            "id": qid,
            "passed": correct,
            "answer": question.get("answer"),
            "message": question.get("explanation", ""),
        })
    return {
        "passed": bool(questions) and ok == len(questions),
        "score": round(ok / len(questions), 3) if questions else 0.0,
        "results": details,
        "output": f"{ok}/{len(questions)} bonnes réponses",
    }
