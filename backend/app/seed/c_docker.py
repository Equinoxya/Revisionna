COURSE = {
    "slug": "docker",
    "title": "Docker et Docker Compose",
    "summary": "Images, couches, construction en plusieurs étapes, volumes, réseaux, isolation et orchestration locale.",
    "category": "DevOps",
    "level": "intermédiaire",
    "icon": "Dk",
    "lessons": [
        {
            "slug": "images-et-couches",
            "title": "Images, couches et cache de construction",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Une **image** est un modèle en lecture seule ; un **conteneur** en est une instance qui tourne. Chaque instruction du Dockerfile crée une **couche**, mise en cache : dès qu'une couche change, toutes les suivantes sont reconstruites.

D'où la règle d'or : **copier les dépendances avant le code**.'''},
                {"type": "code", "lang": "dockerfile", "code": '''FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# 1. les dépendances seules : cache conservé tant que requirements.txt ne bouge pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. le code, qui change à chaque commit
COPY . .

RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]'''},
                {"type": "text", "md": "La **construction en plusieurs étapes** (*multi-stage build*) compile dans une image lourde, puis ne garde que le résultat dans une image légère. C'est le Dockerfile du frontend de cette application : Node construit, nginx sert."},
                {"type": "code", "lang": "dockerfile", "code": '''FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html'''},
                {"type": "callout", "tone": "warn", "md": "`CMD` peut être remplacée depuis la ligne de commande, `ENTRYPOINT` non. Et sans fichier `.dockerignore`, vous envoyez `node_modules` et `.git` au moteur Docker : construction lente, image encombrée, et parfois des secrets embarqués."},
                {"type": "quiz", "id": "q1", "question": "Pourquoi copier requirements.txt avant le reste du code ?", "choices": ["Pour la lisibilité", "Pour conserver le cache des dépendances d'une construction à l'autre", "C'est obligatoire", "Pour réduire le nombre de couches"], "answer": "Pour conserver le cache des dépendances d'une construction à l'autre", "explanation": "Modifier le code n'oblige plus à réinstaller les dépendances."},
                {"type": "quiz", "id": "q2", "question": "Quelle différence entre une image et un conteneur ?", "choices": ["Aucune", "L'image est le modèle, le conteneur l'instance qui tourne", "Le conteneur est plus volumineux", "L'image s'exécute"], "answer": "L'image est le modèle, le conteneur l'instance qui tourne", "explanation": "Comme une classe et ses instances."},
            ],
        },
        {
            "slug": "compose-volumes-reseaux",
            "title": "Compose, volumes, réseaux et isolation",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Compose décrit un ensemble de services dans un seul fichier. Sur le réseau interne, chaque service est joignable par **son nom** : l'API se connecte à `db:5432`, pas à `localhost`."},
                {"type": "code", "lang": "yaml", "code": '''services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?à définir dans .env}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U revisionna"]
      interval: 5s
      retries: 10

  api:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:'''},
                {"type": "callout", "tone": "warn", "md": "`depends_on` seul attend le **démarrage** du conteneur, pas la disponibilité du service. Sans `healthcheck` et `condition: service_healthy`, l'API démarre avant que PostgreSQL accepte les connexions."},
                {"type": "text", "md": "Un **volume** survit au conteneur : c'est le seul moyen de conserver des données. Tout ce qui est écrit ailleurs disparaît avec le conteneur."},
                {"type": "text", "md": '''Un conteneur sert aussi à **enfermer** ce en quoi on n'a pas confiance. Dans cette application, le code que vous soumettez s'exécute dans un service à part (`runner`), réglé ainsi :

```yaml
  runner:
    network_mode: none      # aucun réseau : ni base, ni Internet
    read_only: true         # système de fichiers en lecture seule
    cap_drop: [ALL]         # privilèges retirés
    pids_limit: 256         # pas de bombe de processus
```

Il ne reçoit aucun secret, et l'API lui parle par un simple socket Unix posé sur un volume partagé.'''},
                {"type": "quiz", "id": "q1", "question": "Dans Compose, comment l'API joint-elle la base ?", "choices": ["localhost:5432", "db:5432, le nom du service", "127.0.0.1:5432", "Par l'adresse IP du conteneur"], "answer": "db:5432, le nom du service", "explanation": "Compose fournit une résolution de noms entre services."},
                {"type": "quiz", "id": "q2", "question": "Que perd-on sans volume sur la base ?", "choices": ["Rien", "Les données, à chaque suppression du conteneur", "Seulement les journaux", "La configuration"], "answer": "Les données, à chaque suppression du conteneur", "explanation": "L'espace d'écriture d'un conteneur est éphémère."},
                {"type": "quiz", "id": "q3", "question": "Que garantit `depends_on` sans `condition: service_healthy` ?", "choices": ["Que la base accepte les connexions", "Seulement que le conteneur de la base a démarré", "Que les migrations sont jouées", "Rien du tout"], "answer": "Seulement que le conteneur de la base a démarré", "explanation": "Un conteneur démarré n'est pas encore un service prêt : il faut un `healthcheck`."},
                {"type": "quiz", "id": "q4", "question": "Que provoque `network_mode: none` sur un service ?", "choices": ["Il n'a plus aucun accès réseau", "Il partage le réseau de l'hôte", "Il est plus rapide", "Il ne peut plus écrire sur le disque"], "answer": "Il n'a plus aucun accès réseau", "explanation": "Idéal pour exécuter du code auquel on ne fait pas confiance."},
            ],
        },
        {
            "slug": "commandes-et-depannage",
            "title": "Les commandes du quotidien et le dépannage",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Un conteneur n'est pas une petite machine virtuelle. Une **machine virtuelle** embarque un système d'exploitation complet, noyau compris. Un **conteneur** est un simple processus de l'hôte, isolé par le noyau Linux (espaces de noms, groupes de contrôle) : il démarre en une seconde et ne pèse que ce que pèse l'application.

Conséquence directe : **un conteneur vit tant que son processus principal vit**. Si la commande se termine, le conteneur s'arrête.'''},
                {"type": "code", "lang": "bash", "code": '''docker build -t api:1.4.0 .                 # construire une image
docker run -d --name api -p 8000:5000 api:1.4.0   # lancer (-d : en arrière-plan)
#                          └─ port de l'hôte : port du conteneur

docker ps                 # conteneurs en cours ; -a pour voir aussi les arrêtés
docker logs -f api        # suivre la sortie du processus
docker exec -it api sh    # ouvrir un shell DANS le conteneur
docker inspect api        # toute sa configuration, en JSON
docker stats              # processeur et mémoire, en direct

docker stop api           # SIGTERM, puis SIGKILL après 10 secondes
docker rm api             # supprimer le conteneur arrêté'''},
                {"type": "text", "md": '''Avec Compose, les mêmes gestes s'appliquent à l'ensemble des services :

```bash
docker compose up -d --build     # construire et démarrer
docker compose ps                # l'état de chaque service
docker compose logs -f api       # les journaux d'un service
docker compose exec api sh       # un shell dans le service
docker compose down              # tout arrêter (les volumes sont conservés)
```'''},
                {"type": "text", "md": '''Une image se range dans un **registre** (Docker Hub, GitHub Container Registry) sous un nom complet : `registre/organisation/image:étiquette`.

```bash
docker tag api:1.4.0 ghcr.io/monequipe/api:1.4.0
docker push ghcr.io/monequipe/api:1.4.0
docker pull ghcr.io/monequipe/api:1.4.0
```'''},
                {"type": "callout", "tone": "warn", "md": "L'étiquette `latest` n'est pas « la dernière version » : c'est juste l'étiquette par défaut, et elle change de contenu sans prévenir. En production, on déploie une version **précise** (`1.4.0`, ou l'identifiant du commit) pour savoir exactement ce qui tourne, et pouvoir revenir en arrière."},
                {"type": "text", "md": '''**Le conteneur ne démarre pas ?** Une méthode, toujours la même :

| Symptôme | Où regarder |
|---|---|
| il s'arrête aussitôt | `docker logs` : l'erreur est presque toujours écrite là |
| il redémarre en boucle | `docker ps -a` pour le code de sortie, puis les journaux |
| « connection refused » entre services | utilise-t-on le **nom du service**, et non `localhost` ? |
| le port ne répond pas depuis l'hôte | l'application écoute-t-elle sur `0.0.0.0`, et le port est-il publié (`-p`) ? |
| « permission denied » sur un volume | l'utilisateur du conteneur a-t-il les droits sur le dossier ? |
| le disque est plein | `docker system df`, puis `docker system prune` |

Dans un conteneur, `localhost` désigne **le conteneur lui-même**, pas l'hôte ni le service voisin. Et une application qui écoute sur `127.0.0.1` est injoignable de l'extérieur du conteneur : il faut `0.0.0.0`.'''},
                {"type": "callout", "tone": "info", "md": "Un conteneur est **jetable** : on ne le répare pas à la main avec `docker exec`, on corrige l'image et on le recrée. Toute modification faite à l'intérieur disparaît au prochain démarrage."},
                {"type": "quiz", "id": "q1", "question": "Quelle différence essentielle entre un conteneur et une machine virtuelle ?", "choices": ["Aucune", "Le conteneur partage le noyau de l'hôte, la machine virtuelle embarque le sien", "Le conteneur est plus lourd", "La machine virtuelle démarre plus vite"], "answer": "Le conteneur partage le noyau de l'hôte, la machine virtuelle embarque le sien", "explanation": "D'où un démarrage en une seconde et un poids réduit."},
                {"type": "quiz", "id": "q2", "question": "Que signifie `-p 8000:5000` ?", "choices": ["Le port 5000 de l'hôte vers le 8000 du conteneur", "Le port 8000 de l'hôte vers le 5000 du conteneur", "Deux conteneurs", "Une plage de ports"], "answer": "Le port 8000 de l'hôte vers le 5000 du conteneur", "explanation": "L'ordre est toujours hôte:conteneur."},
                {"type": "quiz", "id": "q3", "question": "Un conteneur s'arrête dès son lancement. Premier réflexe ?", "choices": ["Reconstruire l'image", "Lire `docker logs`", "Redémarrer Docker", "Supprimer les volumes"], "answer": "Lire `docker logs`", "explanation": "Le message d'erreur du processus s'y trouve presque toujours."},
                {"type": "quiz", "id": "q4", "question": "Pourquoi éviter l'étiquette latest en production ?", "choices": ["Elle est plus lente", "On ne sait pas quelle version tourne, ni vers quoi revenir", "Elle est payante", "Elle est interdite par Docker"], "answer": "On ne sait pas quelle version tourne, ni vers quoi revenir", "explanation": "Une étiquette précise rend le déploiement reproductible."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-ordre-dockerfile",
            "title": "Ordonner un Dockerfile pour le cache",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''On vous donne les instructions d'un Dockerfile dans le désordre. Écrivez `ordonner(instructions)`, qui renvoie la liste triée selon la bonne pratique de cache.

Priorité, du plus stable au plus changeant :

1. `FROM`
2. `ENV`
3. `WORKDIR`
4. `COPY requirements.txt` (toute instruction `COPY` contenant `requirements`)
5. `RUN pip install` (toute instruction `RUN`)
6. `COPY . .` (les autres `COPY`)
7. `EXPOSE`
8. `CMD`

À priorité égale, conservez l'ordre d'origine. Une instruction dont le mot-clé n'est pas dans la liste va à la fin.''',
            "starter_code": '''def ordonner(instructions):
    ...
''',
            "solution": '''def ordonner(instructions):
    def rang(ligne):
        mot = ligne.split()[0].upper()
        if mot == "FROM":
            return 0
        if mot == "ENV":
            return 1
        if mot == "WORKDIR":
            return 2
        if mot == "COPY":
            return 3 if "requirements" in ligne else 5
        if mot == "RUN":
            return 4
        if mot == "EXPOSE":
            return 6
        if mot == "CMD":
            return 7
        return 99

    return [ligne for _, _, ligne in sorted(
        ((rang(l), i, l) for i, l in enumerate(instructions)),
        key=lambda item: (item[0], item[1]),
    )]
''',
            "hints": [
                "Écrivez une fonction interne qui donne un rang numérique à chaque instruction.",
                "Pour `COPY`, tout dépend de la présence du mot `requirements` dans la ligne.",
                "Pour un tri qui respecte l'ordre d'origine à rang égal, triez sur `(rang, index)`.",
            ],
            "spec": {"tests": [
                {"name": "ordre_de_base", "code": "ins = ['COPY . .', 'FROM python:3.12-slim', 'RUN pip install -r requirements.txt', 'COPY requirements.txt .']\nassert ordonner(ins) == ['FROM python:3.12-slim', 'COPY requirements.txt .', 'RUN pip install -r requirements.txt', 'COPY . .']"},
                {"name": "cmd_en_dernier", "code": "ins = ['CMD [\"gunicorn\"]', 'FROM python', 'EXPOSE 5000']\nassert ordonner(ins)[-1].startswith('CMD')"},
                {"name": "workdir_et_env", "code": "ins = ['WORKDIR /app', 'ENV A=1', 'FROM python']\nassert ordonner(ins) == ['FROM python', 'ENV A=1', 'WORKDIR /app']"},
                {"name": "inconnue_a_la_fin", "code": "ins = ['LABEL x=1', 'FROM python']\nassert ordonner(ins)[-1] == 'LABEL x=1'"},
                {"name": "ordre_conserve", "code": "ins = ['RUN a', 'RUN b', 'FROM python']\nassert ordonner(ins) == ['FROM python', 'RUN a', 'RUN b']"},
            ]},
        },
        {
            "slug": "quiz-docker",
            "title": "Docker au quotidien",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Les commandes et les notions à avoir en tête.",
            "spec": {"questions": [
                {"id": "1", "question": "Quelle commande construit une image nommée api ?", "choices": ["docker run -t api .", "docker build -t api .", "docker compose exec api", "docker pull api"], "answer": "docker build -t api .", "explanation": "`-t` donne son nom à l'image ; le point désigne le dossier envoyé au moteur."},
                {"id": "2", "question": "À quoi sert le fichier .dockerignore ?", "choices": ["À ignorer des conteneurs", "À exclure des fichiers de la construction", "À masquer des variables", "À désactiver le cache"], "answer": "À exclure des fichiers de la construction", "explanation": "On y met `.git`, `node_modules`, `.venv`, `.env`."},
                {"id": "3", "question": "Pourquoi un utilisateur non root dans l'image ?", "choices": ["Pour la performance", "Pour limiter les dégâts si le conteneur est compromis", "C'est obligatoire", "Pour réduire la taille"], "answer": "Pour limiter les dégâts si le conteneur est compromis", "explanation": "C'est le principe du moindre privilège."},
                {"id": "4", "question": "Que fait `docker compose down -v` ?", "choices": ["Il arrête les services", "Il arrête les services ET supprime les volumes, donc les données", "Il redémarre l'ensemble", "Il affiche les journaux"], "answer": "Il arrête les services ET supprime les volumes, donc les données", "explanation": "`-v` détruit les volumes nommés : c'est irréversible."},
                {"id": "5", "question": "Quel est l'intérêt d'une construction en plusieurs étapes ?", "choices": ["Seulement construire plus vite", "Ne garder que le résultat final, dans une image légère", "Avoir plusieurs conteneurs", "Se passer de volumes"], "answer": "Ne garder que le résultat final, dans une image légère", "explanation": "Les outils de compilation restent dans l'étape de construction."},
                {"id": "6", "question": "Quelle commande ouvre un shell dans un conteneur en cours ?", "choices": ["docker run api sh", "docker exec -it api sh", "docker logs api", "docker attach --shell api"], "answer": "docker exec -it api sh", "explanation": "`exec` lance une commande dans un conteneur existant ; `run` en crée un nouveau."},
                {"id": "7", "question": "Dans un conteneur, que désigne localhost ?", "choices": ["La machine hôte", "Le conteneur lui-même", "Le service db", "Le registre"], "answer": "Le conteneur lui-même", "explanation": "Pour joindre un autre service, on utilise son nom."},
                {"id": "8", "question": "Que fait `docker compose down` (sans option) des volumes nommés ?", "choices": ["Il les supprime", "Il les conserve", "Il les vide", "Il les sauvegarde"], "answer": "Il les conserve", "explanation": "Seule l'option `-v` les détruit."},
                {"id": "9", "question": "Quand un conteneur s'arrête-t-il de lui-même ?", "choices": ["Après une heure", "Quand son processus principal se termine", "Quand on ferme le terminal, toujours", "Jamais"], "answer": "Quand son processus principal se termine", "explanation": "Un conteneur n'est rien d'autre qu'un processus isolé."},
                {"id": "10", "question": "Où ranger une image pour la partager avec la production ?", "choices": ["Dans Git", "Dans un registre d'images", "Par e-mail", "Dans un volume"], "answer": "Dans un registre d'images", "explanation": "Docker Hub ou GitHub Container Registry, par exemple."},
            ]},
        },
    ],
}
