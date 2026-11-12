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
                {"type": "quiz", "id": "q2", "question": "À quoi sert une matrice dans un job ?", "choices": ["À ralentir le pipeline", "À rejouer le même job sur plusieurs versions ou systèmes", "À stocker les secrets", "À fusionner les branches"], "answer": "À rejouer le même job sur plusieurs versions ou systèmes", "explanation": "Par exemple Python 3.12 et 3.13, en parallèle."},
                {"type": "quiz", "id": "q3", "question": "Vous ajoutez une fonctionnalité compatible à la version 1.2.3. Quelle version publier ?", "choices": ["1.2.4", "1.3.0", "2.0.0", "1.2.3-b"], "answer": "1.3.0", "explanation": "Une fonctionnalité compatible incrémente le numéro mineur et remet le correctif à zéro."},
            ],
        },
        {
            "slug": "livraison-et-deploiement-continus",
            "title": "De la CI au déploiement continu",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''La CI répond à « ce code est-il bon ? ». La suite du pipeline répond à « comment arrive-t-il en production ? ». Deux niveaux, qu'on confond souvent :

| | Livraison continue | Déploiement continu |
|---|---|---|
| Ce qui est automatique | tout, jusqu'à un paquet prêt à partir | tout, mise en production comprise |
| La mise en production | un clic humain | aucune intervention |
| Prérequis | une CI fiable | une CI **très** fiable, de la supervision, un retour en arrière rapide |

Dans les deux cas, la règle d'or : **on construit une seule fois**. La même image, identifiée par le commit, traverse la recette puis la production. Reconstruire pour chaque environnement, c'est déployer autre chose que ce qu'on a testé.'''},
                {"type": "code", "lang": "yaml", "code": '''jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test

  image:
    needs: tests                       # pas d'image si les tests échouent
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write                  # le strict nécessaire pour publier
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: ghcr.io/monequipe/api:${{ github.sha }}

  production:
    needs: image
    runs-on: ubuntu-latest
    environment: production            # peut exiger une approbation
    steps:
      - run: ./deployer.sh "${{ github.sha }}"'''},
                {"type": "text", "md": '''Trois idées dans cet exemple :

- l'image est étiquetée par l'**identifiant du commit** (`github.sha`) : on sait toujours quel code tourne ;
- le bloc `permissions` donne au job le **minimum de droits**. Par défaut, mieux vaut tout mettre en lecture seule et n'ouvrir qu'au cas par cas ;
- un **environnement** GitHub porte ses propres secrets et ses règles de protection : approbation obligatoire, branches autorisées.'''},
                {"type": "text", "md": '''Un déploiement automatique n'est acceptable que si le **retour en arrière** l'est aussi. Puisque chaque version est une image étiquetée, revenir en arrière consiste à redéployer l'étiquette précédente : quelques secondes, sans reconstruire.

Après la mise en ligne, le pipeline vérifie que tout va bien : un **test de fumée** appelle `/health` et une ou deux pages clés. S'il échoue, on revient automatiquement à la version précédente.'''},
                {"type": "callout", "tone": "warn", "md": "Une action tierce (`uses: quelquun/action@v1`) est du code qui s'exécute avec vos secrets. N'utilisez que des actions reconnues, et fixez leur version : une étiquette peut être déplacée par son auteur, pas l'identifiant complet d'un commit."},
                {"type": "text", "md": '''La branche `main` se **protège** dans les réglages du dépôt :

- pas d'envoi direct : tout passe par une pull request ;
- les vérifications de la CI doivent être vertes avant la fusion ;
- au moins une relecture approuvée.

Et un pipeline lent finit par être contourné. Pour le garder sous les dix minutes : mettre les dépendances en **cache**, lancer les jobs en **parallèle**, et placer en premier les vérifications les plus rapides (le lint échoue en vingt secondes, inutile d'attendre les tests de bout en bout pour le découvrir).'''},
                {"type": "quiz", "id": "q1", "question": "Quelle différence entre livraison continue et déploiement continu ?", "choices": ["Aucune", "En livraison continue, la mise en production reste une décision humaine", "Le déploiement continu n'a pas de tests", "La livraison continue se passe de CI"], "answer": "En livraison continue, la mise en production reste une décision humaine", "explanation": "En déploiement continu, tout commit validé part seul en production."},
                {"type": "quiz", "id": "q2", "question": "Pourquoi construire l'image une seule fois ?", "choices": ["Pour économiser du disque", "Pour déployer exactement ce qui a été testé", "Parce que Docker l'impose", "Pour éviter les matrices"], "answer": "Pour déployer exactement ce qui a été testé", "explanation": "Une image reconstruite peut embarquer des dépendances différentes."},
                {"type": "quiz", "id": "q3", "question": "Comment revenir rapidement à la version précédente ?", "choices": ["En réécrivant le code", "En redéployant l'image étiquetée de la version précédente", "En supprimant la base", "En relançant la CI trois fois"], "answer": "En redéployant l'image étiquetée de la version précédente", "explanation": "L'image existe déjà dans le registre : rien à reconstruire."},
                {"type": "quiz", "id": "q4", "question": "Quels droits donner à un job de CI ?", "choices": ["Tous, pour éviter les blocages", "Le minimum nécessaire à sa tâche", "Les droits du propriétaire du dépôt", "Aucun droit n'est configurable"], "answer": "Le minimum nécessaire à sa tâche", "explanation": "Un job compromis ne peut alors pas faire plus que ce qu'on lui a accordé."},
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
        {
            "slug": "quiz-cicd",
            "title": "Lire un pipeline",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Le vocabulaire de GitHub Actions et les bonnes pratiques d'un pipeline.",
            "spec": {"questions": [
                {"id": "1", "question": "Que vérifie l'intégration continue ?", "choices": ["Que le site est en ligne", "Que le code se construit et que les tests passent, à chaque envoi", "Que les développeurs sont présents", "Que la base est sauvegardée"], "answer": "Que le code se construit et que les tests passent, à chaque envoi", "explanation": "Un problème détecté tôt coûte beaucoup moins cher à corriger."},
                {"id": "2", "question": "Où déclare-t-on un workflow GitHub Actions ?", "choices": ["Dans le README", "Dans .github/workflows/, en YAML", "Dans package.json", "Dans le Dockerfile"], "answer": "Dans .github/workflows/, en YAML", "explanation": "Chaque fichier du dossier décrit un workflow."},
                {"id": "3", "question": "Par défaut, comment s'exécutent deux jobs sans lien `needs` ?", "choices": ["L'un après l'autre", "En parallèle", "Un seul des deux s'exécute", "Dans l'ordre alphabétique"], "answer": "En parallèle", "explanation": "`needs` impose un ordre ; sans lui, tout part en même temps."},
                {"id": "4", "question": "Un secret s'affiche-t-il dans les journaux d'un job ?", "choices": ["Oui, en clair", "Non, il est masqué", "Seulement sur main", "Seulement en cas d'erreur"], "answer": "Non, il est masqué", "explanation": "Évitez tout de même de le transformer : la version encodée, elle, ne serait pas masquée."},
                {"id": "5", "question": "À quoi sert le cache des dépendances ?", "choices": ["À rendre les tests plus fiables", "À ne pas tout retélécharger à chaque exécution", "À stocker les secrets", "À publier l'image"], "answer": "À ne pas tout retélécharger à chaque exécution", "explanation": "Un pipeline rapide est un pipeline qu'on ne contourne pas."},
                {"id": "6", "question": "Quelle vérification placer en premier dans le pipeline ?", "choices": ["Les tests de bout en bout", "Le lint, qui échoue en quelques secondes", "Le déploiement", "L'audit de licences"], "answer": "Le lint, qui échoue en quelques secondes", "explanation": "On échoue vite sur les erreurs les moins chères à détecter."},
                {"id": "7", "question": "Que vérifie un test de fumée après un déploiement ?", "choices": ["Toute l'application, en détail", "Que le service répond et que les fonctions vitales marchent", "La couverture de code", "Le style du code"], "answer": "Que le service répond et que les fonctions vitales marchent", "explanation": "Rapide et superficiel : il dit s'il faut revenir en arrière tout de suite."},
                {"id": "8", "question": "Avec quoi étiqueter une image construite par la CI ?", "choices": ["latest", "L'identifiant du commit", "La date du jour seulement", "Le nom du développeur"], "answer": "L'identifiant du commit", "explanation": "On relie ainsi chaque image au code exact qui l'a produite."},
            ]},
        },
    ],
}
