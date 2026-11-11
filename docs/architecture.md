# Architecture

## Vue d'ensemble

```
navigateur
   |  (React + React Router, jeton JWT en localStorage)
   v
nginx  --- /api/* --->  gunicorn / Flask
   |                        |
   | fichiers statiques     +--> PostgreSQL (cours, comptes, progression)
                            +--> MongoDB     (journal d'activite, optionnel)
                            +--> Ollama / OpenAI (indices du tuteur)
```

En developpement, nginx est remplace par le proxy du serveur Vite (`vite.config.js`).

## Modele de donnees

| Table | Role |
|---|---|
| `users` | compte, mot de passe hache |
| `courses` | un cours du catalogue |
| `lessons` | lecon, contenu en blocs JSON |
| `exercises` | TP : enonce, type, squelette, specification de correction, solution |
| `progress` | lecon terminee par un utilisateur (+ score du quiz) |
| `submissions` | chaque tentative sur un TP |

Les lecons stockent leur contenu dans une colonne JSON : un bloc a un `type`
(`text`, `code`, `callout`, `quiz`) et ses propres champs. Cela evite une table par type de bloc
et permet d'enrichir le format sans migration.

## Ce qui ne doit jamais sortir du serveur

`models.py` filtre explicitement a la serialisation :

- `_public_block` retire `answer` et `explanation` des blocs quiz ;
- `_public_spec` ne laisse passer que le schema SQL, les intitules de questions et les **noms**
  des tests Python ;
- `Exercise.to_dict` n'expose jamais `solution` ; elle n'est renvoyee qu'apres une soumission reussie.

## Correction des exercices

`services/runner.py` expose trois fonctions :

- `run_python(code, tests)` ecrit le code et les tests dans un fichier temporaire, puis lance
  `python -I services/sandbox.py` en sous-processus avec :
  - un delai d'expiration (`RUNNER_TIMEOUT`, 8 s par defaut),
  - `RLIMIT_CPU` (5 s), `RLIMIT_AS` (512 Mo), `RLIMIT_NPROC`,
  - un environnement reduit (`PATH` minimal),
  - un controle statique prealable refusant `import os`, `subprocess`, `__import__`, `eval`...

  Le harness renvoie une ligne JSON : resultat par test, sortie standard, erreur de chargement.

- `run_sql(query, spec)` cree une base SQLite **en memoire**, joue le schema de l'exercice,
  execute la requete attendue puis celle de l'eleve et compare les lignes (ordre ignore sauf si
  `ordered` est vrai).

- `run_quiz(answers, spec)` compare les reponses aux valeurs attendues.

Limite assumee : le bac a sable Python repose sur des limites de processus, pas sur une isolation
noyau. Pour un deploiement ouvert au public, faites tourner `sandbox.py` dans un conteneur jetable
sans reseau (`docker run --rm --network none --memory 256m`).

## Authentification

JWT signe (HS256), duree de vie 12 h, transmis en `Authorization: Bearer`.
La deconnexion ajoute le `jti` du jeton a une liste de revocation en memoire :
suffisant pour un projet pedagogique, a remplacer par Redis des qu'il y a plusieurs workers
persistants (sinon un worker peut ignorer une revocation enregistree par un autre).

## Degradation gracieuse

Deux dependances sont optionnelles et ne doivent jamais faire echouer une requete :

- **MongoDB** : `services/activity.py` teste la connexion une fois, puis journalise en
  best-effort ; toute exception est avalee avec un avertissement.
- **IA** : `services/ai.py` leve `AIUnavailable`, interceptee par la vue qui renvoie alors
  l'indice statique de l'exercice.

## Pipeline CI

`.github/workflows/ci.yml` lance quatre jobs :

1. `backend` : ruff + pytest sur Python 3.12 et 3.13 (matrice) ;
2. `content` : `scripts/verifier_contenu.py`, qui verifie que **chaque solution de reference passe
   les tests de son propre exercice** — un garde-fou contre les enonces incoherents ;
3. `frontend` : eslint + build Vite ;
4. `images` : build des deux images Docker, uniquement si les trois precedents sont verts (`needs`).
