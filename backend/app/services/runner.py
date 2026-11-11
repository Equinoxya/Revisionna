"""Correction automatique des exercices : Python, SQL, quiz."""
from __future__ import annotations

import json
import os
import pathlib
import resource
import sqlite3
import subprocess
import sys
import tempfile

HARNESS = pathlib.Path(__file__).with_name("sandbox.py")

FORBIDDEN = (
    "import os", "import sys", "import subprocess", "import socket",
    "import shutil", "__import__", "open(", "eval(", "exec(",
)


def _limits():  # pragma: no cover - execute dans le sous-processus
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))


def static_check(code: str) -> str | None:
    """Garde-fou pedagogique : refuse les appels systeme evidents."""
    lowered = code.lower()
    for needle in FORBIDDEN:
        if needle in lowered:
            return f"Appel interdit dans le bac a sable : `{needle}`"
    return None


def run_python(code: str, tests: list[dict], timeout: int = 8) -> dict:
    blocked = static_check(code)
    if blocked:
        return {"passed": False, "score": 0.0, "output": blocked, "results": []}

    with tempfile.TemporaryDirectory() as tmp:
        payload_path = os.path.join(tmp, "payload.json")
        with open(payload_path, "w", encoding="utf-8") as fh:
            json.dump({"code": code, "tests": tests}, fh)

        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(HARNESS), payload_path],
                capture_output=True, text=True, timeout=timeout, cwd=tmp,
                preexec_fn=_limits if hasattr(os, "fork") else None,
                env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"},
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False, "score": 0.0, "results": [],
                "output": f"Temps depasse ({timeout}s) : boucle infinie ?",
            }

    try:
        data = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        if proc.returncode and proc.returncode < 0:
            # tue par un signal : limite de CPU ou de memoire atteinte
            return {
                "passed": False, "score": 0.0, "results": [],
                "output": "Temps depasse ou memoire epuisee : boucle infinie ?",
            }
        return {
            "passed": False, "score": 0.0, "results": [],
            "output": (proc.stderr or proc.stdout or "Erreur inconnue")[-2000:],
        }

    if data.get("error"):
        return {
            "passed": False, "score": 0.0, "results": [],
            "output": "Votre code n'a pas pu etre charge :\n" + data["error"],
        }

    results = data["results"]
    ok = sum(1 for r in results if r["passed"])
    total = len(results) or 1
    lines = [f"{'OK  ' if r['passed'] else 'FAIL'} {r['name']}"
             + (f" -> {r['message']}" if r["message"] else "")
             for r in results]
    if data.get("stdout"):
        lines.append("\n--- sortie de votre code ---\n" + data["stdout"][-1500:])

    return {
        "passed": ok == len(results) and bool(results),
        "score": round(ok / total, 3),
        "results": results,
        "output": "\n".join(lines),
    }


def run_sql(query: str, spec: dict) -> dict:
    """Execute la requete de l'eleve sur une base SQLite jetee apres coup."""
    schema = spec.get("schema", "")
    expected_query = spec.get("expected_query", "")
    ordered = bool(spec.get("ordered", False))

    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(schema)
        try:
            expected = conn.execute(expected_query).fetchall()
        except sqlite3.Error as exc:  # erreur cote enonce
            return {"passed": False, "score": 0.0, "output": f"Exercice mal configure : {exc}"}

        try:
            got = conn.execute(query).fetchall()
        except sqlite3.Error as exc:
            return {"passed": False, "score": 0.0, "output": f"Erreur SQL : {exc}"}
    finally:
        conn.close()

    same = got == expected if ordered else sorted(map(str, got)) == sorted(map(str, expected))
    output = (
        f"Lignes attendues : {len(expected)} | obtenues : {len(got)}\n"
        f"Votre resultat : {got[:10]}\n"
    )
    if not same:
        output += f"Resultat attendu : {expected[:10]}"
    return {"passed": same, "score": 1.0 if same else 0.0, "output": output.strip(), "rows": got[:50]}


def run_quiz(answers: dict, spec: dict) -> dict:
    """answers = {question_id: valeur}."""
    questions = spec.get("questions", [])
    details, ok = [], 0
    for question in questions:
        qid = str(question.get("id"))
        given = answers.get(qid)
        correct = given == question.get("answer")
        ok += int(correct)
        details.append({
            "id": qid,
            "passed": correct,
            "message": question.get("explanation", ""),
        })
    total = len(questions) or 1
    return {
        "passed": ok == len(questions) and bool(questions),
        "score": round(ok / total, 3),
        "results": details,
        "output": f"{ok}/{len(questions)} bonnes reponses",
    }
