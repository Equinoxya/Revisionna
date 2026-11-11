#!/usr/bin/env python3
"""Verifie que chaque solution de reference passe les tests de son exercice.

Utilise en CI : un enonce dont la solution echoue est un bug de contenu.
Usage : python scripts/verifier_contenu.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.seed import CATALOG  # noqa: E402
from app.services import runner  # noqa: E402


def main() -> int:
    echecs = []

    for cours in CATALOG:
        for exercice in cours["exercises"]:
            reference = f"{cours['slug']}/{exercice['slug']}"
            kind = exercice.get("kind", "python")

            if kind == "python":
                resultat = runner.run_python(
                    exercice["solution"], exercice["spec"]["tests"], timeout=20
                )
            elif kind == "sql":
                resultat = runner.run_sql(exercice["solution"], exercice["spec"])
            elif kind == "quiz":
                reponses = {q["id"]: q["answer"] for q in exercice["spec"]["questions"]}
                resultat = runner.run_quiz(reponses, exercice["spec"])
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
        print(f"{len(echecs)} exercice(s) en echec :")
        for reference, sortie in echecs:
            print(f"\n--- {reference} ---\n{sortie[:1000]}")
        return 1

    total = sum(len(c["exercises"]) for c in CATALOG)
    print(f"{total} exercices verifies, tout est coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
