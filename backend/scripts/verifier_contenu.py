#!/usr/bin/env python3
"""Vérifie que chaque solution de référence passe les tests de son exercice.

Utilisé en CI : un énoncé dont la solution échoue est une erreur de contenu.
Usage : python scripts/verifier_contenu.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.seed import CATALOG  # noqa: E402
from app.services.runner import run_quiz  # noqa: E402
from sandbox import core  # noqa: E402


def main() -> int:
    echecs = []

    for cours in CATALOG:
        for exercice in cours["exercises"]:
            reference = f"{cours['slug']}/{exercice['slug']}"
            kind = exercice.get("kind", "python")

            if kind == "python":
                resultat = core.run_python(
                    exercice["solution"], exercice["spec"]["tests"], timeout=20
                )
            elif kind == "sql":
                resultat = core.run_sql(exercice["solution"], exercice["spec"])
            elif kind == "quiz":
                reponses = {q["id"]: q["answer"] for q in exercice["spec"]["questions"]}
                resultat = run_quiz(reponses, exercice["spec"])
            else:
                echecs.append((reference, f"type inconnu : {kind}"))
                continue

            if resultat["passed"]:
                print(f"OK   {reference}")
            else:
                print(f"KO   {reference}")
                echecs.append((reference, resultat.get("output", "")))

    print()
    if echecs:
        print(f"{len(echecs)} exercice(s) en échec :")
        for reference, sortie in echecs:
            print(f"\n--- {reference} ---\n{sortie[:1000]}")
        return 1

    total = sum(len(c["exercises"]) for c in CATALOG)
    print(f"{total} exercices vérifiés, tout est cohérent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
