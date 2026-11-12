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
                {"type": "quiz", "id": "q3", "question": "Quels sont les trois piliers de l'observabilité ?", "choices": ["Journaux, métriques, traces", "Tests, lint, couverture", "CPU, mémoire, disque", "Dev, recette, production"], "answer": "Journaux, métriques, traces", "explanation": "Ce qui s'est passé, des mesures dans le temps, et le parcours d'une requête."},
            ],
        },
        {
            "slug": "https-securite-et-sauvegardes",
            "title": "HTTPS, durcissement et sauvegardes",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''En HTTP, tout circule **en clair** : mots de passe, jetons, contenu des pages. **HTTPS** ajoute TLS, qui apporte trois garanties :

- la **confidentialité** : personne ne lit l'échange en chemin ;
- l'**intégrité** : personne ne le modifie ;
- l'**authenticité** : le **certificat** prouve que le serveur est bien celui du domaine.

Un certificat est délivré par une **autorité de certification** reconnue par les navigateurs. *Let's Encrypt* en fournit gratuitement, valables 90 jours, renouvelés automatiquement par un outil comme `certbot` ou par un proxy comme Caddy ou Traefik.'''},
                {"type": "code", "lang": "nginx", "code": '''server {
    listen 80;
    server_name revisionna.example;
    return 301 https://$host$request_uri;        # tout le trafic passe en HTTPS
}

server {
    listen 443 ssl;
    server_name revisionna.example;

    ssl_certificate     /etc/letsencrypt/live/revisionna.example/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/revisionna.example/privkey.pem;

    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Content-Security-Policy "default-src 'self'" always;

    location /api/ {
        proxy_pass http://api:5000;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}'''},
                {"type": "text", "md": '''Les **en-têtes de sécurité** demandent au navigateur de se protéger lui-même :

| En-tête | Effet |
|---|---|
| `Strict-Transport-Security` (HSTS) | le navigateur n'utilisera plus jamais HTTP pour ce site |
| `Content-Security-Policy` (CSP) | liste les sources autorisées pour les scripts, les images, les styles |
| `X-Content-Type-Options: nosniff` | le navigateur ne devine pas le type d'un fichier |

Ouvrez `frontend/nginx-securite.conf` : cette application les envoie tous.'''},
                {"type": "text", "md": '''**Durcir** un serveur, c'est réduire ce qu'un attaquant peut atteindre :

1. n'ouvrir que les ports nécessaires (80, 443, et SSH) ;
2. SSH par clé uniquement, connexion directe de root interdite ;
3. appliquer les mises à jour de sécurité, automatiquement si possible ;
4. un compte de service sans privilèges pour chaque application ;
5. limiter le débit sur les routes sensibles (connexion, inscription) pour freiner les attaques par force brute.'''},
                {"type": "text", "md": '''Une **sauvegarde** n'existe que si elle a été **restaurée avec succès**. La règle **3-2-1** :

- **3** copies des données ;
- sur **2** supports différents ;
- dont **1** hors site.

Deux chiffres se décident avant l'incident, pas pendant :

- le **RPO** (perte de données maximale admissible) : « on accepte de perdre au plus une heure de données » fixe la fréquence des sauvegardes ;
- le **RTO** (durée maximale d'interruption) : « le service doit revenir en moins de deux heures » fixe les moyens de restauration.'''},
                {"type": "code", "lang": "bash", "code": '''# sauvegarder
pg_dump --format=custom revisionna > /srv/sauvegardes/revisionna-$(date +%F).dump

# restaurer dans une base de test, et VÉRIFIER
createdb restauration_test
pg_restore --dbname=restauration_test /srv/sauvegardes/revisionna-2026-11-12.dump
psql restauration_test -c "SELECT count(*) FROM users;"'''},
                {"type": "callout", "tone": "warn", "md": "Une sauvegarde rangée sur le même disque que la base ne protège ni d'une panne du disque, ni d'un rançongiciel, ni d'un `rm -rf` malheureux. Et une sauvegarde qui contient des données personnelles doit être **chiffrée** et supprimée à l'expiration de sa durée de conservation."},
                {"type": "quiz", "id": "q1", "question": "Que prouve le certificat d'un site en HTTPS ?", "choices": ["Que le site est sans bogue", "Que le serveur est bien celui du domaine", "Que le site est rapide", "Que le site respecte le RGPD"], "answer": "Que le serveur est bien celui du domaine", "explanation": "TLS ajoute à cela la confidentialité et l'intégrité des échanges."},
                {"type": "quiz", "id": "q2", "question": "Que demande l'en-tête Strict-Transport-Security ?", "choices": ["De compresser les réponses", "De n'utiliser que HTTPS pour ce site à l'avenir", "De bloquer les cookies", "De mettre les pages en cache"], "answer": "De n'utiliser que HTTPS pour ce site à l'avenir", "explanation": "Même si l'utilisateur tape une adresse en http://."},
                {"type": "quiz", "id": "q3", "question": "Que signifie la règle 3-2-1 ?", "choices": ["3 serveurs, 2 bases, 1 proxy", "3 copies, 2 supports, 1 hors site", "3 tests, 2 relectures, 1 fusion", "3 jours, 2 heures, 1 minute"], "answer": "3 copies, 2 supports, 1 hors site", "explanation": "Aucun incident isolé ne doit pouvoir détruire toutes les copies."},
                {"type": "quiz", "id": "q4", "question": "Comment savoir qu'une sauvegarde est valable ?", "choices": ["Le fichier existe", "Sa taille est non nulle", "On l'a restaurée et vérifiée", "La tâche planifiée n'a pas signalé d'erreur"], "answer": "On l'a restaurée et vérifiée", "explanation": "Une sauvegarde jamais restaurée n'est qu'un espoir."},
                {"type": "quiz", "id": "q5", "question": "« On accepte de perdre au plus une heure de données » : de quoi s'agit-il ?", "choices": ["Du RTO", "Du RPO", "Du TTL", "Du SLA"], "answer": "Du RPO", "explanation": "Le RPO borne la perte de données ; le RTO borne la durée d'interruption."},
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
                {"id": "6", "question": "Peut-on utiliser `flask run` en production ?", "choices": ["Oui", "Non : il faut un serveur d'application comme gunicorn", "Oui, avec DEBUG actif", "Oui, sur le port 80"], "answer": "Non : il faut un serveur d'application comme gunicorn", "explanation": "Le serveur de développement n'est ni performant ni sûr."},
                {"id": "7", "question": "Quand jouer les migrations de base lors d'une mise en ligne ?", "choices": ["Après avoir ouvert le trafic", "Avant d'ouvrir le trafic, dans une étape à part", "Jamais en production", "Au premier appel d'un utilisateur"], "answer": "Avant d'ouvrir le trafic, dans une étape à part", "explanation": "Le nouveau code ne doit pas démarrer sur un ancien schéma."},
                {"id": "8", "question": "Combien de temps un certificat Let's Encrypt est-il valable ?", "choices": ["7 jours", "90 jours", "1 an", "10 ans"], "answer": "90 jours", "explanation": "D'où l'importance d'un renouvellement automatique."},
                {"id": "9", "question": "Quels ports laisser ouverts sur un serveur web ?", "choices": ["Tous", "80, 443 et SSH", "Seulement 5432", "Aucun"], "answer": "80, 443 et SSH", "explanation": "Tout le reste, base de données comprise, reste sur le réseau interne."},
                {"id": "10", "question": "Où ranger la copie hors site d'une sauvegarde ?", "choices": ["Sur le même disque", "Dans un autre lieu ou chez un autre hébergeur", "Dans le dépôt Git", "Dans /tmp"], "answer": "Dans un autre lieu ou chez un autre hébergeur", "explanation": "Un incendie ou un rançongiciel ne doit pas emporter toutes les copies."},
            ]},
        },
    ],
}
