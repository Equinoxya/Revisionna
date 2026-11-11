#!/usr/bin/env python3
"""Test de bout en bout d'une instance qui tourne (bibliothèque standard uniquement).

    python3 scripts/smoke.py [http://localhost:8080]

Parcourt l'essentiel comme le ferait un navigateur (cookie de session, jeton
CSRF), puis vérifie que le code soumis par un élève est bien enfermé : pas de
réseau, pas de secret, un compte Unix jetable. Utilisé par la CI après
`docker compose up`. Code de sortie non nul au premier échec.
"""
import http.cookiejar
import json
import os
import secrets
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080").rstrip("/")
INVITE = os.environ.get("INVITE_CODE", "")
MOT_DE_PASSE = "ardoise-magique-" + secrets.token_hex(3) + "7"

cookies = http.cookiejar.CookieJar()
navigateur = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
echecs = 0


def appel(methode, chemin, corps=None):
    en_tetes = {"Accept": "application/json"}
    donnees = None
    if methode != "GET":
        en_tetes["Content-Type"] = "application/json"
        donnees = json.dumps(corps or {}).encode()
        jeton = next((c.value for c in cookies if c.name == "revisionna_csrf"), None)
        if jeton:
            en_tetes["X-CSRF-Token"] = jeton
    requete = urllib.request.Request(BASE + chemin, data=donnees, headers=en_tetes, method=methode)
    try:
        with navigateur.open(requete, timeout=60) as reponse:
            return reponse.status, reponse.headers, reponse.read()
    except urllib.error.HTTPError as erreur:
        return erreur.code, erreur.headers, erreur.read()


def api(methode, chemin, corps=None):
    statut, _, brut = appel(methode, "/api" + chemin, corps)
    try:
        return statut, json.loads(brut or b"{}")
    except ValueError:
        return statut, {}


def verifier(libelle, condition, detail=""):
    global echecs
    if not condition:
        echecs += 1
    print(f"  {'ok   ' if condition else 'ÉCHEC'} {libelle}" + (f"  [{detail}]" if detail and not condition else ""))


print(f"Instance testée : {BASE}")

print("Santé et en-têtes")
statut, sante = api("GET", "/health")
verifier("l'API répond", statut == 200, f"{statut} {sante}")
verifier("la base répond", sante.get("database") == "ok", str(sante))
verifier("le correcteur est isolé", sante.get("runner") == "isolé", str(sante.get("runner")))
statut, en_tetes, page = appel("GET", "/")
csp = en_tetes.get("Content-Security-Policy", "")
verifier("la page d'accueil est servie", statut == 200 and b'id="root"' in page, str(statut))
verifier("politique de sécurité du contenu stricte", "script-src 'self'" in csp and "unsafe" not in csp, csp)
verifier("pas d'affichage dans une autre page", en_tetes.get("X-Frame-Options") == "DENY")
statut, en_tetes, _ = appel("GET", "/api/health")
verifier("réponses de l'API jamais mises en cache", en_tetes.get("Cache-Control") == "no-store")
verifier("aucune origine tierce autorisée", "Access-Control-Allow-Origin" not in en_tetes)

print("Compte et session")
etiquette = secrets.token_hex(3)
compte = {"email": f"smoke-{etiquette}@exemple.fr", "username": f"Smoke_{etiquette}",
          "password": MOT_DE_PASSE, "accept_terms": True}
statut, meta = api("GET", "/meta")
if meta.get("invite_required"):
    statut, corps = api("POST", "/auth/register", compte)
    verifier("inscription refusée sans code d'invitation", statut == 400, f"{statut} {corps}")
    compte["invite_code"] = INVITE
statut, corps = api("POST", "/auth/register", compte)
verifier("inscription", statut == 201, f"{statut} {corps}")
session = next((c for c in cookies if c.name == "revisionna_session"), None)
verifier("cookie de session HttpOnly", bool(session) and session.has_nonstandard_attr("HttpOnly"))
verifier("le jeton ne passe pas par JavaScript", "access_token" not in corps)
statut, corps = api("GET", "/auth/me")
verifier("session reconnue", statut == 200 and corps.get("user", {}).get("username") == compte["username"])

print("Leçon et exercices")
statut, corps = api("POST", "/courses/python/lessons/types-et-structures/complete", {"answers": {"q1": "tuple"}})
verifier("leçon corrigée", statut == 200 and corps.get("score") == 0.5, f"{statut} {corps}")
statut, corps = api("GET", "/courses/python/exercises/tp-statistiques")
exercice = corps.get("exercise", {})
verifier("énoncé sans la solution", statut == 200 and "solution" not in exercice)
solution = (
    "def moyenne(notes):\n    return sum(notes) / len(notes) if notes else 0.0\n\n"
    "def admis(notes, seuil=10):\n    return [n for n in notes if n >= seuil]\n\n"
    "def repartition(notes):\n    b = {'faible': 0, 'moyen': 0, 'bon': 0}\n"
    "    for n in notes:\n        b['faible' if n < 8 else 'moyen' if n < 14 else 'bon'] += 1\n    return b\n"
)
statut, corps = api("POST", f"/exercises/{exercice.get('id')}/submit", {"code": solution})
verifier("TP Python corrigé dans le conteneur isolé", statut == 200 and corps.get("passed") is True, f"{statut} {corps}")
statut, corps = api("GET", "/courses/sql/exercises/tp-left-join")
statut, corps = api("POST", f"/exercises/{corps.get('exercise', {}).get('id')}/submit",
                    {"code": "SELECT e.nom FROM etudiants e WHERE NOT EXISTS "
                             "(SELECT 1 FROM inscriptions i WHERE i.etudiant_id = e.id AND i.note >= 12)"})
verifier("TP SQL corrigé", statut == 200 and corps.get("passed") is True, f"{statut} {corps}")

print("Enfermement du code des élèves")
sonde = '''
import os, pathlib, socket
print("UID", os.getuid())
def essai(nom, action):
    try:
        action()
        print(nom, "POSSIBLE")
    except Exception as erreur:
        print(nom, "refusé", type(erreur).__name__)
essai("RESEAU_INTERNET", lambda: socket.create_connection(("1.1.1.1", 443), timeout=3))
essai("RESEAU_BASE", lambda: socket.create_connection(("db", 5432), timeout=3))
essai("RESEAU_API", lambda: socket.create_connection(("api", 5000), timeout=3))
essai("ENVIRON_SERVEUR", lambda: pathlib.Path("/proc/1/environ").read_bytes())
essai("SIGNAL_SERVEUR", lambda: os.kill(1, 0))
essai("ECRITURE_SYSTEME", lambda: pathlib.Path("/opt/intrus").write_text("x"))
print("SECRETS", [k for k in os.environ if "SECRET" in k or "PASSWORD" in k or "DATABASE" in k])
'''
statut, corps = api("POST", f"/exercises/{exercice.get('id')}/submit", {"code": sonde})
sortie = corps.get("stdout", "")
uid = next((int(l.split()[1]) for l in sortie.splitlines() if l.startswith("UID ")), -1)
verifier("exécuté sous un compte jetable (ni root, ni celui de l'API)", uid >= 20000, f"uid={uid} sortie={sortie!r} {corps.get('output')!r}")
for nom, libelle in [("RESEAU_INTERNET", "aucun accès à Internet"), ("RESEAU_BASE", "aucun accès à la base"),
                     ("RESEAU_API", "aucun accès à l'API"), ("ENVIRON_SERVEUR", "environnement du serveur illisible"),
                     ("SIGNAL_SERVEUR", "impossible de signaler le serveur"), ("ECRITURE_SYSTEME", "système de fichiers en lecture seule")]:
    verifier(libelle, f"{nom} refusé" in sortie, sortie.replace("\n", " | "))
verifier("aucun secret dans son environnement", "SECRETS []" in sortie, sortie.replace("\n", " | "))

print("Droits sur les données et déconnexion")
statut, _, brut = appel("GET", "/api/me/export")
export = json.loads(brut) if statut == 200 else {}
verifier("export de mes données", statut == 200 and len(export.get("soumissions", [])) == 3, f"{statut}")
ancien = session.value if session else ""
statut, _ = api("POST", "/auth/logout")
verifier("déconnexion", statut == 200)
requete = urllib.request.Request(BASE + "/api/auth/me", headers={"Cookie": f"revisionna_session={ancien}"})
try:
    urllib.request.urlopen(requete, timeout=20)
    rejoue = 200
except urllib.error.HTTPError as erreur:
    rejoue = erreur.code
verifier("l'ancien jeton est refusé après déconnexion", rejoue == 401, str(rejoue))
statut, _ = api("POST", "/auth/login", {"identifier": compte["username"].upper(), "password": MOT_DE_PASSE})
verifier("reconnexion par nom d'utilisateur, sans tenir compte de la casse", statut == 200, str(statut))
statut, corps = api("DELETE", "/me", {"password": MOT_DE_PASSE})
verifier("suppression du compte", statut == 200, f"{statut} {corps}")
statut, _ = api("POST", "/auth/login", {"identifier": compte["email"], "password": MOT_DE_PASSE})
verifier("le compte supprimé n'existe plus", statut == 401, str(statut))

print(f"\n{'Tout est bon.' if not echecs else str(echecs) + ' vérification(s) en échec.'}")
sys.exit(1 if echecs else 0)
