"""Harness execute dans un sous-processus : lance le code de l'eleve puis les tests.

Entree  : un fichier JSON {"code": "...", "tests": [{"name": ..., "code": ...}]}
Sortie  : une ligne JSON sur stdout {"results": [...], "stdout": "..."}
"""
import io
import json
import sys
import traceback
from contextlib import redirect_stdout


def main() -> int:
    payload = json.load(open(sys.argv[1], encoding="utf-8"))
    namespace: dict = {"__name__": "solution"}
    buffer = io.StringIO()
    results = []

    try:
        with redirect_stdout(buffer):
            exec(compile(payload["code"], "solution.py", "exec"), namespace)
    except Exception:
        print(json.dumps({
            "results": [],
            "stdout": buffer.getvalue(),
            "error": traceback.format_exc(limit=3),
        }))
        return 0

    for test in payload["tests"]:
        entry = {"name": test["name"], "passed": True, "message": ""}
        try:
            with redirect_stdout(buffer):
                exec(compile(test["code"], f"test_{test['name']}.py", "exec"), dict(namespace))
        except AssertionError as exc:
            entry["passed"] = False
            entry["message"] = str(exc) or "assertion echouee"
        except Exception as exc:  # noqa: BLE001
            entry["passed"] = False
            entry["message"] = f"{type(exc).__name__}: {exc}"
        results.append(entry)

    print(json.dumps({"results": results, "stdout": buffer.getvalue(), "error": None}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
