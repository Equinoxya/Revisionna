"""Processus enfant du bac à sable : exécute le code d'un élève puis les tests.

Lancé par `sandbox.core` dans un sous-processus limité (CPU, mémoire, fichiers,
nombre de processus) et, dans le service isolé, sous un compte Unix jetable.

Entrée : le chemin d'un fichier JSON `{"kind": "python" | "sql", ...}`.
Sortie : une ligne JSON, la dernière écrite sur la sortie standard.

Le code de l'élève tourne dans ce même processus : il peut donc fausser sa
propre note. Ce n'est pas un enjeu ici ; ce qui compte, c'est qu'il ne puisse
rien atteindre d'autre, et cela relève de l'isolation mise en place autour.
"""
import io
import json
import sqlite3
import sys
import traceback
from contextlib import redirect_stdout

MAX_STDOUT = 20_000   # caractères de sortie conservés
MAX_ROWS = 500        # lignes SQL renvoyées


class LimitedBuffer(io.StringIO):
    """Tampon qui cesse d'enregistrer au-delà d'une taille donnée."""

    def write(self, text):
        room = MAX_STDOUT - self.tell()
        if room > 0:
            super().write(text[:room])
        return len(text)


def _describe(exc: BaseException) -> str:
    """Trace limitée au code de l'élève (sans les lignes du harness)."""
    tb = exc.__traceback__
    tb = tb.tb_next if tb else None
    return "".join(traceback.format_exception(type(exc), exc, tb, limit=6)).strip()


def run_python(payload: dict) -> dict:
    namespace: dict = {"__name__": "solution"}
    buffer = LimitedBuffer()

    try:
        with redirect_stdout(buffer):
            exec(compile(payload["code"], "solution.py", "exec"), namespace)
    except BaseException as exc:  # noqa: BLE001 - y compris SystemExit
        return {"results": [], "stdout": buffer.getvalue(), "error": _describe(exc)}

    results = []
    for test in payload["tests"]:
        entry = {"name": test["name"], "passed": True, "message": ""}
        try:
            with redirect_stdout(buffer):
                exec(compile(test["code"], f"test_{test['name']}.py", "exec"), dict(namespace))
        except AssertionError as exc:
            entry["passed"] = False
            entry["message"] = str(exc) or "résultat différent de celui attendu"
        except BaseException as exc:  # noqa: BLE001
            entry["passed"] = False
            entry["message"] = f"{type(exc).__name__} : {exc}"
        results.append(entry)

    return {"results": results, "stdout": buffer.getvalue(), "error": None}


_REFUSED = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA}


def _authorizer(action, arg1, arg2, _db, _source):
    """Refuse ce qui sort de la base jetable : ATTACH, PRAGMA, extensions."""
    if action in _REFUSED:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() == "load_extension":
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def _plain(rows) -> list:
    return [
        [value.hex() if isinstance(value, (bytes, bytearray)) else value for value in row]
        for row in rows
    ]


def run_sql(payload: dict) -> dict:
    conn = sqlite3.connect(":memory:")
    try:
        try:
            conn.executescript(payload.get("schema", ""))
            expected = conn.execute(payload["expected_query"]).fetchmany(MAX_ROWS + 1)
        except sqlite3.Error as exc:
            return {"error": f"Exercice mal configuré : {exc}", "config": True}

        conn.set_authorizer(_authorizer)
        try:
            cursor = conn.execute(payload["query"])
            rows = cursor.fetchmany(MAX_ROWS + 1)
            columns = [column[0] for column in cursor.description or []]
        except (sqlite3.Error, sqlite3.Warning) as exc:
            return {"error": f"Erreur SQL : {exc}"}
    finally:
        conn.close()

    return {
        "error": None,
        "columns": columns,
        "expected": _plain(expected[:MAX_ROWS]),
        "rows": _plain(rows[:MAX_ROWS]),
        "truncated": len(rows) > MAX_ROWS,
    }


def main() -> int:
    with open(sys.argv[1], encoding="utf-8") as handle:
        payload = json.load(handle)
    runner = run_sql if payload.get("kind") == "sql" else run_python
    result = runner(payload)
    sys.__stdout__.write("\n" + json.dumps(result) + "\n")
    sys.__stdout__.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
