# Revisionna

Application de revision : **lecons interactives** d'un cote, **TP corriges automatiquement** de l'autre,
sur les 14 cours de l'annee (Python, Flask, Django, React, SQL, NoSQL, Machine Learning,
integration IA, systeme Linux, reseaux, bases du DevOps, Docker, CI/CD, deploiement).

L'application est elle-meme un cas d'etude : elle utilise la plupart des technos qu'elle enseigne.

| | |
|---|---|
| Backend | Flask 3 (application factory + blueprints), SQLAlchemy, JWT |
| Frontend | React 18 + Vite + React Router |
| Base SQL | SQLite en dev, PostgreSQL en Docker |
| Base NoSQL | MongoDB (journal d'activite, optionnel) |
| IA | Ollama (local) ou OpenAI, avec repli hors ligne |
| Conteneurs | Dockerfile multi-stage + Docker Compose |
| CI | GitHub Actions (lint, tests, verification du contenu, build des images) |

## Fonctionnalites

- **Comptes** : inscription, connexion (email ou pseudo), deconnexion avec revocation du jeton.
- **Lecons interactives** : contenu en blocs (texte, code, encarts, quiz corriges). Les reponses
  des quiz ne sont **jamais** envoyees au navigateur avant validation.
- **TP pratiques**, de trois types :
  - `python` : votre code est execute dans un sous-processus isole et confronte a une batterie de tests ;
  - `sql` : votre requete tourne sur une base SQLite jetable et son resultat est compare a celui attendu ;
  - `quiz` : QCM corrige cote serveur.
- **Indices progressifs** puis **tuteur IA** (Ollama ou OpenAI) qui donne un indice, jamais la solution.
- **Tableau de bord** : progression par cours, historique des soumissions.

## Demarrage rapide (Docker)

```bash
docker compose up --build
```

- Interface : <http://localhost:8080>
- API : <http://localhost:5000/api/health>

La base est creee et le contenu charge automatiquement au demarrage du service `api`.

## Demarrage en local (sans Docker)

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # ajustez SECRET_KEY et JWT_SECRET_KEY

flask --app wsgi:app init-db    # cree les tables
flask --app wsgi:app seed       # charge les 14 cours
flask --app wsgi:app run        # http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

Le serveur de dev Vite relaie `/api` vers Flask : pas de configuration CORS a gerer.

## Tests et qualite

```bash
cd backend
pytest                          # 29 tests : auth, contenu, correction, progression
ruff check .
python scripts/verifier_contenu.py   # chaque solution de reference passe ses propres tests

cd ../frontend
npm run lint
npm run build
```

## Activer l'IA

Dans `backend/.env` :

```bash
# modele local
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# ou API distante
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Sans configuration, `AI_PROVIDER` vide, l'application reste pleinement utilisable : le tuteur
renvoie des indices heuristiques et les indices statiques de chaque exercice restent disponibles.

## Structure

```
backend/
  app/
    __init__.py        application factory
    config.py          configuration par variables d'environnement
    models.py          User, Course, Lesson, Exercise, Progress, Submission
    api/               auth.py, content.py, workspace.py, system.py
    services/          runner.py (correction), sandbox.py, ai.py, activity.py
    seed/              un module par cours (c_python.py, c_flask.py, ...)
  scripts/             verifier_contenu.py
  tests/               pytest
frontend/
  src/
    lib/               api.js, AuthContext.jsx
    components/        Layout, ProtectedRoute, Markdown, Quiz
    pages/             Connexion, Inscription, TableauDeBord, Catalogue, Cours, Lecon, Exercice
compose.yaml
.github/workflows/ci.yml
docs/
```

## API

| Methode | Route | Description |
|---|---|---|
| POST | `/api/auth/register` | creation de compte |
| POST | `/api/auth/login` | connexion (email ou pseudo) |
| POST | `/api/auth/logout` | revocation du jeton |
| GET | `/api/auth/me` | profil courant |
| GET | `/api/courses` | catalogue |
| GET | `/api/courses/<slug>` | detail d'un cours |
| GET | `/api/courses/<c>/lessons/<l>` | lecon (sans les reponses de quiz) |
| POST | `/api/courses/<c>/lessons/<l>/complete` | correction du quiz + progression |
| GET | `/api/courses/<c>/exercises/<e>` | enonce (sans la solution) |
| POST | `/api/exercises/<id>/submit` | correction automatique |
| POST | `/api/exercises/<id>/hint` | indice du tuteur IA |
| GET | `/api/exercises/<id>/submissions` | historique |
| GET | `/api/me/dashboard` | progression globale |
| GET | `/api/health` | sonde pour Docker / CI |

## Securite

Voir [docs/architecture.md](docs/architecture.md) pour le detail. En resume :

- mots de passe haches (Werkzeug/PBKDF2), jamais stockes en clair ;
- reponses de quiz et solutions filtrees cote serveur avant serialisation ;
- code des eleves execute dans un sous-processus avec limites CPU/memoire, delai d'expiration et
  liste noire d'appels systeme. **Ce bac a sable convient a un usage pedagogique local ; pour une
  exposition publique, isolez l'execution dans un conteneur jetable dedie.**

## Ajouter un cours

Creez `backend/app/seed/c_moncours.py` sur le modele des autres, ajoutez-le a `CATALOG` dans
`backend/app/seed/__init__.py`, puis relancez `flask --app wsgi:app seed`. Le chargement est
idempotent : il met a jour l'existant sans toucher aux comptes ni a la progression.

### Ajouter la video d'une lecon

Chaque lecon reserve un emplacement video en tete de page (« Video explicative a venir »).
Pour la renseigner, ajoutez la cle `"video"` a la lecon dans son fichier de cours, puis rejouez le `seed` :

```python
{
    "slug": "shell-et-arborescence",
    "title": "Le shell et l'arborescence",
    "video": "https://exemple.fr/videos/shell.mp4",   # fichier MP4 ou WebM, servi en HTTPS
    ...
}
```
