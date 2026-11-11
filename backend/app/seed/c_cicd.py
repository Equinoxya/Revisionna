COURSE = {
    "slug": "ci-cd",
    "title": "CI/CD avec GitHub Actions",
    "summary": "Pipeline, jobs, matrices, cache, secrets, portes de qualité, audit des dépendances et numérotation des versions.",
    "category": "DevOps",
    "level": "intermédiaire",
    "icon": "CI",
    "lessons": [
        {
            "slug": "pipeline-github-actions",
            "title": "Anatomie d'un pipeline",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''**Intégration continue** (CI) : à chaque envoi de code, on vérifie automatiquement qu'il se construit, que le style est respecté et que les tests passent. **Déploiement continu** (CD) : si tout est vert, on livre.

Le vocabulaire de GitHub Actions : un *workflow* contient des *jobs* (lancés en parallèle par défaut), et chaque job une suite d'étapes (*steps*) exécutées l'une après l'autre.'''},
                {"type": "code", "lang": "yaml", "code": '''name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r backend/requirements-dev.txt
      - run: ruff check backend
      - run: pytest backend

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: "22"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
        working-directory: frontend
      - run: npm run build
        working-directory: frontend'''},
                {"type": "text", "md": "Les deux jobs tournent **en parallèle** : la réponse arrive plus vite. Un job de déploiement, lui, déclare `needs: [backend, frontend]` pour attendre les deux."},
                {"type": "callout", "tone": "warn", "md": "Un **secret** (`${{ secrets.X }}`) n'apparaît jamais dans les journaux, et n'est pas transmis aux workflows déclenchés depuis un fork. N'écrivez jamais une clé dans le fichier YAML."},
                {"type": "callout", "tone": "info", "md": "La CI ne vérifie que ce qui est **dans le dépôt**. Un fichier présent sur votre machine mais ignoré par `.gitignore` fait passer vos tests en local… et casser la construction pour tous les autres. D'où l'intérêt de tester à partir d'un clone neuf."},
                {"type": "quiz", "id": "q1", "question": "Comment obliger un job à en attendre un autre ?", "choices": ["depends_on", "needs", "after", "requires"], "answer": "needs", "explanation": "`needs: [autre_job]` crée la dépendance."},
                {"type": "quiz", "id": "q2", "question": "Que fait `npm ci`, à la différence de `npm install` ?", "choices": ["Rien de différent", "Il installe exactement ce que décrit package-lock.json", "Il installe pour tout le système", "Il met les dépendances à jour"], "answer": "Il installe exactement ce que décrit package-lock.json", "explanation": "En CI, on veut la même installation à chaque fois, pas des mises à jour surprises."},
            ],
        },
        {
            "slug": "qualite-et-versions",
            "title": "Portes de qualité, audit et versions",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": '''Une **porte de qualité** bloque la fusion tant qu'un critère n'est pas rempli : tests verts, couverture minimale, style propre, relecture approuvée. Sur GitHub, cela se règle dans les règles de protection de branche.

L'ordre des étapes compte : les vérifications rapides d'abord (style, tests unitaires), les lentes ensuite (intégration, bout en bout). On échoue le plus tôt possible.'''},
                {"type": "code", "lang": "yaml", "code": '''    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
      fail-fast: false
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}'''},
                {"type": "text", "md": '''Vos dépendances vieillissent sans que votre code change : des failles y sont découvertes chaque semaine. Un **audit automatique** les signale :

```bash
pip-audit -r backend/requirements.txt
npm audit --audit-level=high
```

Cette application le lance à chaque envoi de code et une fois par semaine.'''},
                {"type": "text", "md": '''**Numérotation sémantique** (SemVer) : `MAJEUR.MINEUR.CORRECTIF`.

- correctif : une correction compatible (1.2.3 → 1.2.4) ;
- mineur : une fonctionnalité compatible (1.2.3 → 1.3.0) ;
- majeur : une rupture de compatibilité (1.2.3 → 2.0.0).'''},
                {"type": "quiz", "id": "q1", "question": "Vous supprimez un champ dans la réponse d'une API. Quelle version publier après la 1.2.3 ?", "choices": ["1.2.4", "1.3.0", "2.0.0", "1.2.3-beta"], "answer": "2.0.0", "explanation": "C'est une rupture pour ceux qui utilisent l'API : le numéro majeur augmente."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-semver",
            "title": "Calculer la prochaine version",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Écrivez `prochaine_version(version, type_changement)` :

- `version` est une chaîne `"MAJEUR.MINEUR.CORRECTIF"` ;
- `type_changement` vaut `"correctif"`, `"mineur"` ou `"majeur"` ;
- une version mineure remet le correctif à 0 ; une version majeure remet le mineur et le correctif à 0 ;
- un type inconnu lève `ValueError` ;
- une version mal formée (pas exactement 3 segments, ou un segment qui n'est pas un nombre) lève `ValueError`.''',
            "starter_code": '''def prochaine_version(version, type_changement):
    ...
''',
            "solution": '''def prochaine_version(version, type_changement):
    segments = version.split(".")
    if len(segments) != 3 or not all(s.isdigit() for s in segments):
        raise ValueError(f"version invalide : {version}")
    majeur, mineur, correctif = (int(s) for s in segments)

    if type_changement == "correctif":
        correctif += 1
    elif type_changement == "mineur":
        mineur, correctif = mineur + 1, 0
    elif type_changement == "majeur":
        majeur, mineur, correctif = majeur + 1, 0, 0
    else:
        raise ValueError(f"type inconnu : {type_changement}")

    return f"{majeur}.{mineur}.{correctif}"
''',
            "hints": [
                "`version.split('.')`, puis vérifiez la longueur et `isdigit()`.",
                "Validez avant de calculer : une version invalide ne doit rien incrémenter.",
                "N'oubliez pas de remettre à zéro les segments de droite.",
            ],
            "spec": {"tests": [
                {"name": "correctif", "code": "assert prochaine_version('1.2.3', 'correctif') == '1.2.4'"},
                {"name": "mineur", "code": "assert prochaine_version('1.2.3', 'mineur') == '1.3.0'"},
                {"name": "majeur", "code": "assert prochaine_version('1.2.3', 'majeur') == '2.0.0'"},
                {"name": "type_inconnu", "code": "try:\n    prochaine_version('1.2.3', 'patchouli')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('ValueError attendue')"},
                {"name": "version_incomplete", "code": "try:\n    prochaine_version('1.2', 'mineur')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('ValueError attendue')"},
                {"name": "segment_non_numerique", "code": "try:\n    prochaine_version('1.x.3', 'mineur')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('ValueError attendue')"},
            ]},
        },
        {
            "slug": "tp-porte-qualite",
            "title": "Une porte de qualité",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Un pipeline doit décider s'il peut déployer.

`evaluer(rapport, seuil_couverture=80)` reçoit un dictionnaire, par exemple :

```python
{"tests": {"passes": 42, "echoues": 0}, "couverture": 86.2, "lint": 0, "revues": 1}
```

Renvoyez `{"deployable": bool, "raisons": [...]}`, où `raisons` liste les blocages dans cet ordre :

1. `"tests en échec"` si `echoues > 0`
2. `"aucun test"` si `passes == 0` et `echoues == 0`
3. `"couverture insuffisante"` si `couverture < seuil_couverture`
4. `"erreurs de style"` si `lint > 0`
5. `"relecture manquante"` si `revues < 1`

`deployable` n'est vrai que si `raisons` est vide. Une clé absente vaut 0.''',
            "starter_code": '''def evaluer(rapport, seuil_couverture=80):
    ...
''',
            "solution": '''def evaluer(rapport, seuil_couverture=80):
    tests = rapport.get("tests", {}) or {}
    passes = tests.get("passes", 0)
    echoues = tests.get("echoues", 0)
    raisons = []

    if echoues > 0:
        raisons.append("tests en échec")
    if passes == 0 and echoues == 0:
        raisons.append("aucun test")
    if rapport.get("couverture", 0) < seuil_couverture:
        raisons.append("couverture insuffisante")
    if rapport.get("lint", 0) > 0:
        raisons.append("erreurs de style")
    if rapport.get("revues", 0) < 1:
        raisons.append("relecture manquante")

    return {"deployable": not raisons, "raisons": raisons}
''',
            "hints": [
                "Utilisez partout `.get(cle, 0)` pour gérer les clés absentes.",
                "Ajoutez les raisons dans l'ordre exact de l'énoncé.",
                "`not raisons` vaut `True` quand la liste est vide.",
            ],
            "spec": {"tests": [
                {"name": "tout_vert", "code": "r = {'tests': {'passes': 10, 'echoues': 0}, 'couverture': 90, 'lint': 0, 'revues': 1}\nassert evaluer(r) == {'deployable': True, 'raisons': []}"},
                {"name": "tests_echoues", "code": "r = {'tests': {'passes': 9, 'echoues': 1}, 'couverture': 90, 'lint': 0, 'revues': 1}\nres = evaluer(r)\nassert res['deployable'] is False and res['raisons'] == ['tests en échec']"},
                {"name": "aucun_test", "code": "r = {'tests': {'passes': 0, 'echoues': 0}, 'couverture': 90, 'lint': 0, 'revues': 1}\nassert evaluer(r)['raisons'] == ['aucun test']"},
                {"name": "couverture", "code": "r = {'tests': {'passes': 5, 'echoues': 0}, 'couverture': 42.0, 'lint': 0, 'revues': 1}\nassert evaluer(r)['raisons'] == ['couverture insuffisante']"},
                {"name": "style_et_relecture", "code": "r = {'tests': {'passes': 5, 'echoues': 0}, 'couverture': 90, 'lint': 3, 'revues': 0}\nassert evaluer(r)['raisons'] == ['erreurs de style', 'relecture manquante']"},
                {"name": "rapport_vide", "code": "res = evaluer({})\nassert res['deployable'] is False and res['raisons'] == ['aucun test', 'couverture insuffisante', 'relecture manquante']"},
                {"name": "seuil_personnalise", "code": "r = {'tests': {'passes': 5, 'echoues': 0}, 'couverture': 50, 'lint': 0, 'revues': 1}\nassert evaluer(r, seuil_couverture=50)['deployable'] is True"},
            ]},
        },
    ],
}
