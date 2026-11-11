"""Lance le harness dans un sous-processus limité et met en forme le résultat.

Deux niveaux de protection :

1. toujours : limites de ressources (CPU, mémoire, taille des fichiers,
   nombre de processus), délai d'expiration, environnement vidé, groupe de
   processus tué à la fin ;
2. dans le service isolé (lancé en root dans son conteneur) : chaque travail
   tourne sous un compte Unix jetable (`identity`), sans réseau ni secrets.

Le niveau 1 seul ne suffit pas à exécuter le code d'inconnus : voir
docs/securite.md.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import resource
import shutil
import signal
import subprocess
import sys
import tempfile

HARNESS = pathlib.Path(__file__).with_name("harness.py")

CPU_SECONDS = 5
MEMORY_BYTES = 384 * 1024 * 1024
FILE_BYTES = 1024 * 1024
MAX_PROCESSES = 32
MAX_OPEN_FILES = 64
DEFAULT_TIMEOUT = 8

_ENV = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "LANG": "C.UTF-8",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONDONTWRITEBYTECODE": "1",
}


def _apply_limits() -> None:  # pragma: no cover - exécuté dans l'enfant
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_BYTES, FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_NPROC, (MAX_PROCESSES, MAX_PROCESSES))
    resource.setrlimit(resource.RLIMIT_NOFILE, (MAX_OPEN_FILES, MAX_OPEN_FILES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _kill_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def _kill_uid(uid: int) -> None:
    """Tue tout ce qui tourne encore sous le compte jetable (appelé par root)."""
    for _ in range(5):
        found = False
        for entry in os.scandir("/proc"):
            if not entry.name.isdigit():
                continue
            try:
                if entry.stat().st_uid == uid:
                    os.kill(int(entry.name), signal.SIGKILL)
                    found = True
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
        if not found:
            return


def execute(
    payload: dict,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    identity: tuple[int, int] | None = None,
    base_dir: str | None = None,
) -> dict:
    """Exécute un travail. Renvoie `{"status": "ok", "data": {...}}` ou un échec.

    `identity` = (uid, gid) du compte jetable ; nécessite d'être root.
    """
    jobdir = pathlib.Path(tempfile.mkdtemp(prefix="job-", dir=base_dir))
    status = "ok"
    try:
        payload_path = jobdir / "payload.json"
        payload_path.write_text(json.dumps(payload), encoding="utf-8")

        account: dict = {}
        if identity is not None:
            uid, gid = identity
            os.chown(payload_path, uid, gid)
            os.chown(jobdir, uid, gid)
            account = {"user": uid, "group": gid, "extra_groups": []}

        # Les sorties sont lues via ces descripteurs, jamais rouvertes par leur
        # chemin : l'enfant ne peut donc pas nous faire lire un autre fichier.
        with tempfile.TemporaryFile() as out:
            proc = subprocess.Popen(
                [sys.executable, "-I", str(HARNESS), str(payload_path)],
                stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.DEVNULL,
                cwd=jobdir, env=_ENV, start_new_session=True,
                preexec_fn=_apply_limits, **account,
            )
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                status = "timeout"
            finally:
                _kill_group(proc.pid)
                if identity is not None:
                    _kill_uid(identity[0])
                proc.wait()

            flooded = out.seek(0, os.SEEK_END) >= FILE_BYTES
            out.seek(0)
            raw = out.read(FILE_BYTES).decode("utf-8", "replace")
    finally:
        shutil.rmtree(jobdir, ignore_errors=True)

    if status == "timeout":
        return {"status": "timeout", "detail": f"Temps dépassé ({timeout} s) : boucle infinie ?"}
    if proc.returncode < 0 or flooded:
        return {
            "status": "killed",
            "detail": "Exécution interrompue : limite de temps de calcul, de mémoire "
                      "ou de taille de sortie atteinte.",
        }

    lines = [line for line in raw.splitlines() if line.strip()]
    try:
        data = json.loads(lines[-1])
    except (IndexError, ValueError):
        data = None
    if not isinstance(data, dict):
        # Typiquement : le code a quitté le processus avant la fin des tests.
        return {
            "status": "crash",
            "detail": "Le correcteur n'a reçu aucun résultat : votre code a-t-il "
                      "interrompu le programme (os._exit, etc.) ?",
        }
    return {"status": "ok", "data": data}


def _failure(outcome: dict) -> dict:
    return {"passed": False, "score": 0.0, "results": [], "output": outcome["detail"].strip()}


def run_python(code: str, tests: list[dict], **options) -> dict:
    outcome = execute({"kind": "python", "code": code, "tests": tests}, **options)
    if outcome["status"] != "ok":
        return _failure(outcome)

    data = outcome["data"]
    stdout = str(data.get("stdout") or "")[:20_000]
    if data.get("error"):
        return {
            "passed": False, "score": 0.0, "results": [], "stdout": stdout,
            "output": "Votre code n'a pas pu être chargé :\n" + str(data["error"])[:3000],
        }

    # Le résultat vient d'un processus que l'élève contrôle : on ne garde que
    # ce qui correspond aux tests demandés, avec des types sûrs.
    reported = {
        str(item.get("name")): item
        for item in data.get("results") or []
        if isinstance(item, dict)
    }
    results = []
    for test in tests:
        item = reported.get(test["name"], {})
        results.append({
            "name": test["name"],
            "passed": item.get("passed") is True,
            "message": str(item.get("message") or ("" if item else "test non exécuté"))[:500],
        })

    ok = sum(1 for item in results if item["passed"])
    lines = [
        f"{'OK   ' if item['passed'] else 'ÉCHEC'} {item['name']}"
        + (f" → {item['message']}" if item["message"] else "")
        for item in results
    ]
    if stdout.strip():
        lines.append("\n--- sortie de votre code ---\n" + stdout[-1500:])

    return {
        "passed": bool(results) and ok == len(results),
        "score": round(ok / len(results), 3) if results else 0.0,
        "results": results,
        "stdout": stdout,
        "output": "\n".join(lines),
    }


def _sort_key(row: list) -> str:
    return json.dumps(
        [round(value, 6) if isinstance(value, float) else value for value in row],
        sort_keys=True, default=str,
    )


def _same_value(a, b) -> bool:
    numbers = (int, float)
    if isinstance(a, numbers) and isinstance(b, numbers) and not isinstance(a, bool):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
    return a == b


def same_rows(expected: list, rows: list, *, ordered: bool) -> bool:
    """Compare deux résultats SQL, avec une tolérance sur les flottants."""
    if len(expected) != len(rows):
        return False
    if not ordered:
        expected, rows = sorted(expected, key=_sort_key), sorted(rows, key=_sort_key)
    return all(
        len(left) == len(right) and all(_same_value(x, y) for x, y in zip(left, right, strict=True))
        for left, right in zip(expected, rows, strict=True)
    )


def run_sql(query: str, spec: dict, **options) -> dict:
    outcome = execute(
        {
            "kind": "sql",
            "query": query,
            "schema": spec.get("schema", ""),
            "expected_query": spec.get("expected_query", ""),
        },
        **options,
    )
    if outcome["status"] != "ok":
        return _failure(outcome)

    data = outcome["data"]
    if data.get("error"):
        return {"passed": False, "score": 0.0, "results": [], "output": str(data["error"])[:1500]}

    expected, rows = data.get("expected") or [], data.get("rows") or []
    same = same_rows(expected, rows, ordered=bool(spec.get("ordered")))

    output = f"Lignes attendues : {len(expected)} · obtenues : {len(rows)}"
    if data.get("truncated"):
        output += " (résultat tronqué)"
    result = {
        "passed": same,
        "score": 1.0 if same else 0.0,
        "results": [],
        "output": output,
        "columns": [str(name) for name in data.get("columns") or []][:30],
        "rows": rows[:50],
    }
    if not same:
        result["expected_rows"] = expected[:10]
    return result
