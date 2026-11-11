#!/usr/bin/env python3
"""Crée le fichier .env de Compose, avec des secrets aléatoires.

    python3 scripts/generer_env.py          (ou : make env)

N'écrase jamais un fichier existant : vos secrets et votre base y sont liés.
"""
import pathlib
import secrets
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
CIBLE = RACINE / ".env"

MODELE = """\
# Secrets de Revisionna, générés le jour de l'installation.
# NE PAS versionner, NE PAS partager. Les perdre, c'est perdre l'accès à la base.

SECRET_KEY={secret}
JWT_SECRET_KEY={jwt}
POSTGRES_PASSWORD={postgres}
MONGO_PASSWORD={mongo}

# --- Inscriptions -----------------------------------------------------------
# Code à donner à vos camarades : sans lui, impossible de créer un compte.
# Laissez vide pour ouvrir les inscriptions à tout le monde.
INVITE_CODE={invite}

# --- Accès ------------------------------------------------------------------
WEB_PORT=8080
# false : essai local en HTTP (http://localhost:8080).
# En ligne, servez le site en HTTPS (voir compose.https.yaml) ; les cookies sont
# alors marqués « Secure » automatiquement, quel que soit ce réglage.
COOKIE_SECURE=false
# Nombre de proxys devant l'API : 1 (nginx seul), 2 avec compose.https.yaml.
TRUSTED_PROXIES=1
# Avec compose.https.yaml : le nom de domaine du site.
SITE_DOMAIN=

# --- Durées de conservation (voir docs/conformite-rgpd.md) --------------------
INACTIVE_ACCOUNT_MONTHS=24
ACTIVITY_RETENTION_DAYS=180

# --- Tuteur IA : vide (désactivé), ollama (local) ou openai (distant) ---------
# Avec openai, le code des élèves part aux États-Unis : l'interface les en
# avertit, et vous devez avoir accepté l'accord de traitement des données d'OpenAI.
AI_PROVIDER=
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
"""


def main() -> int:
    if CIBLE.exists():
        print(f"{CIBLE.name} existe déjà : rien n'a été modifié.")
        return 0

    invite = f"promo-{secrets.token_hex(4)}"
    contenu = MODELE.format(
        secret=secrets.token_urlsafe(48),
        jwt=secrets.token_urlsafe(48),
        postgres=secrets.token_urlsafe(24),
        mongo=secrets.token_urlsafe(24),
        invite=invite,
    )
    CIBLE.touch(mode=0o600)
    CIBLE.write_text(contenu, encoding="utf-8")
    print(f"{CIBLE.name} créé (lisible par vous seul).")
    print(f"Code d'invitation à transmettre à vos camarades : {invite}")
    print("Suite : docker compose up -d --build, puis http://localhost:8080")
    return 0


if __name__ == "__main__":
    sys.exit(main())
