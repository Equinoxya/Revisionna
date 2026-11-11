COURSE = {
    "slug": "deploiement",
    "title": "Déploiement en production",
    "summary": "Serveur d'application, proxy inverse, secrets, HTTPS, migrations, observabilité, stratégies de mise en ligne et obligations légales.",
    "category": "DevOps",
    "level": "avancé",
    "icon": "Dp",
    "lessons": [
        {
            "slug": "du-dev-a-la-prod",
            "title": "Du serveur de développement à la production",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Le serveur intégré à Flask ou à Django (`flask run`, `runserver`) n'est **pas fait pour la production** : un seul processus, aucune protection.

La chaîne classique :

`navigateur → nginx (HTTPS, fichiers statiques) → gunicorn (plusieurs workers) → votre application → base de données`'''},
                {"type": "code", "lang": "bash", "code": '''# repère courant : 2 x nombre de cœurs + 1 workers
gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 60 --access-logfile - wsgi:app'''},
                {"type": "text", "md": '''Parmi les « douze facteurs », ceux qui comptent le plus au quotidien :

1. la configuration vit dans l'environnement, jamais dans le code ;
2. les processus sont sans état : avec plusieurs workers, ce qui est gardé en mémoire par l'un est invisible pour les autres (une liste de sessions révoquées, par exemple, doit aller en base) ;
3. les journaux partent sur la sortie standard, et la plateforme les collecte ;
4. le développement ressemble à la production, d'où l'intérêt de Docker.'''},
                {"type": "callout", "tone": "warn", "md": "Trois réglages que cherche tout attaquant : le mode `DEBUG` resté actif, une clé secrète laissée à sa valeur d'exemple, et un site en HTTP. Cette application refuse de démarrer en production avec une clé absente, trop courte ou recopiée d'un exemple."},
                {"type": "text", "md": "Les **migrations** se jouent avant d'ouvrir le trafic, dans une étape à part (`flask db upgrade`, `manage.py migrate`), jamais au démarrage de chaque worker."},
                {"type": "quiz", "id": "q1", "question": "Pourquoi placer nginx devant gunicorn ?", "choices": ["Pour exécuter Python", "Pour le HTTPS, les fichiers statiques et la résistance aux connexions lentes", "Pour la base de données", "Cela ne sert jamais"], "answer": "Pour le HTTPS, les fichiers statiques et la résistance aux connexions lentes", "explanation": "Un proxy inverse prend en charge ce qu'un serveur d'application fait mal."},
                {"type": "quiz", "id": "q2", "question": "Où ranger la configuration propre à un environnement ?", "choices": ["Dans le code, derrière un if", "Dans des variables d'environnement", "Dans un commentaire", "Dans la base"], "answer": "Dans des variables d'environnement", "explanation": "Le même programme, une configuration différente : c'est le troisième facteur."},
            ],
        },
        {
            "slug": "observabilite-et-releases",
            "title": "Observabilité, mises en ligne et obligations",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "L'observabilité repose sur trois piliers : les **journaux** (ce qui s'est passé), les **métriques** (des mesures dans le temps), les **traces** (le parcours d'une requête). Et un minimum vital : une adresse `/api/health` que la plateforme interroge."},
                {"type": "code", "lang": "python", "code": '''@bp.get("/health")
def health():
    checks = {"api": "ok"}
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "erreur"
        return jsonify(checks), 503
    return jsonify(checks)'''},
                {"type": "text", "md": '''Les stratégies de mise en ligne :

- **remplacement** : on arrête, on remplace. Simple, avec une coupure ;
- **progressive** (*rolling*) : les instances sont remplacées une à une. Pas de coupure, mais deux versions cohabitent ;
- **bleu/vert** : deux environnements complets, on bascule le trafic d'un coup, et on revient en arrière tout aussi vite ;
- **canari** : 5 % du trafic sur la nouvelle version, on observe, puis on étend.'''},
                {"type": "callout", "tone": "info", "md": "Les mises en ligne progressives imposent un schéma de base **compatible avec l'ancienne version** : on ajoute une colonne facultative, on déploie le code, on remplit, puis on durcit la contrainte dans une version suivante. Jamais tout d'un coup."},
                {"type": "text", "md": '''Mettre un site en ligne, c'est aussi une responsabilité. Dès que d'autres personnes y créent un compte, il faut en France :

- des **mentions légales** (qui édite, qui héberge) ;
- une **politique de confidentialité** : quelles données, pourquoi, combien de temps ;
- les moyens d'**exporter, corriger et supprimer** ses données (RGPD) ;
- le **HTTPS**, et des mots de passe hachés.

Cette application sert d'exemple : voyez les pages en pied de site, la page « Mon compte », et `docs/conformite-rgpd.md`.'''},
                {"type": "quiz", "id": "q1", "question": "Quelle stratégie permet un retour en arrière presque instantané ?", "choices": ["Le remplacement", "Le bleu/vert", "La mise en ligne progressive", "Aucune"], "answer": "Le bleu/vert", "explanation": "L'ancien environnement est toujours là : il suffit de rebasculer le trafic."},
                {"type": "quiz", "id": "q2", "question": "Que doit répondre /health quand la base est injoignable ?", "choices": ["200", "404", "503", "500"], "answer": "503", "explanation": "503, service indisponible : la plateforme cesse d'envoyer du trafic à cette instance."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-config-env",
            "title": "Charger une configuration d'environnement",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Écrivez `charger_config(env, defauts=None)`, qui construit la configuration d'une application à partir d'un dictionnaire de variables d'environnement.

Les règles :

- `DEBUG` n'est vrai que si la valeur vaut `"1"`, `"true"`, `"yes"` ou `"on"`, sans tenir compte de la casse. Absente, elle vaut `False` ;
- `PORT` est un entier, `5000` par défaut ; une valeur non numérique lève `ValueError` ;
- `DATABASE_URL` est obligatoire : absente ou vide, elle lève `KeyError` ;
- `WORKERS` est un entier, `1` par défaut ;
- les clés de `defauts` servent de valeurs de repli, avant d'appliquer ces règles ;
- le résultat est un dictionnaire aux clés en minuscules : `debug`, `port`, `database_url`, `workers`.''',
            "starter_code": '''def charger_config(env, defauts=None):
    ...
''',
            "solution": '''VRAI = {"1", "true", "yes", "on"}


def charger_config(env, defauts=None):
    source = {**(defauts or {}), **env}

    url = (source.get("DATABASE_URL") or "").strip()
    if not url:
        raise KeyError("DATABASE_URL est obligatoire")

    brut_port = str(source.get("PORT", 5000))
    if not brut_port.isdigit():
        raise ValueError(f"PORT invalide : {brut_port}")

    brut_workers = str(source.get("WORKERS", 1))
    if not brut_workers.isdigit():
        raise ValueError(f"WORKERS invalide : {brut_workers}")

    return {
        "debug": str(source.get("DEBUG", "")).strip().lower() in VRAI,
        "port": int(brut_port),
        "database_url": url,
        "workers": int(brut_workers),
    }
''',
            "hints": [
                "`{**defauts, **env}` : l'environnement réel l'emporte sur les valeurs de repli.",
                "Vérifiez `DATABASE_URL` avant tout le reste.",
                "`str(valeur).isdigit()` fonctionne aussi bien avec une chaîne qu'avec un entier.",
            ],
            "spec": {"tests": [
                {"name": "minimal", "code": "c = charger_config({'DATABASE_URL': 'sqlite:///x.db'})\nassert c == {'debug': False, 'port': 5000, 'database_url': 'sqlite:///x.db', 'workers': 1}"},
                {"name": "debug_variantes", "code": "for v in ['1', 'true', 'TRUE', 'yes', 'on']:\n    assert charger_config({'DATABASE_URL': 'x', 'DEBUG': v})['debug'] is True\nassert charger_config({'DATABASE_URL': 'x', 'DEBUG': 'false'})['debug'] is False"},
                {"name": "base_obligatoire", "code": "try:\n    charger_config({})\nexcept KeyError:\n    pass\nelse:\n    raise AssertionError('KeyError attendue')"},
                {"name": "port_invalide", "code": "try:\n    charger_config({'DATABASE_URL': 'x', 'PORT': 'abc'})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('ValueError attendue')"},
                {"name": "valeurs_de_repli", "code": "c = charger_config({'PORT': '8000'}, defauts={'DATABASE_URL': 'sqlite:///d.db'})\nassert c['port'] == 8000 and c['database_url'] == 'sqlite:///d.db'"},
                {"name": "environnement_prioritaire", "code": "c = charger_config({'DATABASE_URL': 'reel'}, defauts={'DATABASE_URL': 'defaut'})\nassert c['database_url'] == 'reel'"},
            ]},
        },
        {
            "slug": "quiz-deploiement",
            "title": "Avant d'appuyer sur le bouton",
            "kind": "quiz",
            "difficulty": "moyen",
            "statement": "Les décisions à prendre avant une mise en production.",
            "spec": {"questions": [
                {"id": "1", "question": "En mise en ligne progressive, vous ajoutez une colonne obligatoire sans valeur par défaut. Que se passe-t-il ?", "choices": ["Rien", "L'ancienne version échoue dès qu'elle insère une ligne", "La migration échoue toujours", "Les données sont perdues"], "answer": "L'ancienne version échoue dès qu'elle insère une ligne", "explanation": "Ajoutez la colonne facultative, déployez, remplissez, puis durcissez la contrainte."},
                {"id": "2", "question": "Combien de workers gunicorn sur 2 cœurs ?", "choices": ["1", "Environ 5 (2 x cœurs + 1)", "50", "Autant que de requêtes"], "answer": "Environ 5 (2 x cœurs + 1)", "explanation": "C'est un repère, à ajuster selon que l'application attend surtout le réseau ou calcule."},
                {"id": "3", "question": "Qui doit servir les fichiers statiques du frontend ?", "choices": ["La base de données", "nginx ou un réseau de diffusion de contenu", "gunicorn", "Un volume Python"], "answer": "nginx ou un réseau de diffusion de contenu", "explanation": "Un serveur d'application Python sert mal les fichiers statiques."},
                {"id": "4", "question": "Que journaliser en production ?", "choices": ["Tout, mots de passe compris", "Les événements utiles et les erreurs, jamais les secrets ni des données personnelles superflues", "Rien", "Seulement les erreurs 500"], "answer": "Les événements utiles et les erreurs, jamais les secrets ni des données personnelles superflues", "explanation": "Un journal est lu par beaucoup de monde et conservé longtemps."},
                {"id": "5", "question": "Des camarades créent un compte sur votre site. Qu'est-ce qui devient obligatoire ?", "choices": ["Rien, c'est un projet d'école", "Les informer de l'usage de leurs données et leur permettre de les supprimer", "Leur faire signer un contrat papier", "Déclarer le site en préfecture"], "answer": "Les informer de l'usage de leurs données et leur permettre de les supprimer", "explanation": "Le RGPD s'applique dès qu'on traite les données d'autres personnes, quelle que soit la taille du projet."},
            ]},
        },
    ],
}
