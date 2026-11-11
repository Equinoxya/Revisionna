COURSE = {
    "slug": "flask",
    "title": "Flask : micro-framework web",
    "summary": "Routes, blueprints, fabrique d'application, JSON, erreurs et tests avec le client de test.",
    "category": "Backend",
    "level": "intermédiaire",
    "icon": "Fl",
    "lessons": [
        {
            "slug": "routes-et-requetes",
            "title": "Routes, requêtes, réponses",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": "Flask associe une **URL** à une **fonction de vue**. C'est le décorateur `@app.route` (ou ses raccourcis `@app.get`, `@app.post`) qui fait l'enregistrement."},
                {"type": "code", "lang": "python", "code": '''from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/api/cours/<slug>")
def detail(slug):
    return jsonify({"slug": slug})

@app.post("/api/cours")
def creer():
    data = request.get_json(silent=True) or {}
    if not data.get("titre"):
        return jsonify({"error": "titre requis"}), 400
    return jsonify(data), 201'''},
                {"type": "callout", "tone": "info", "md": "`request.get_json(silent=True)` évite une erreur 400 brutale quand le corps n'est pas du JSON : c'est vous qui décidez du message d'erreur."},
                {"type": "text", "md": "Les codes de retour ont un sens : `200` lecture, `201` création, `400` données invalides, `401` non authentifié, `403` interdit, `404` introuvable, `409` conflit, `429` trop de requêtes."},
                {"type": "quiz", "id": "q1", "question": "Quel code HTTP pour une création réussie ?", "choices": ["200", "201", "204", "302"], "answer": "201", "explanation": "201 Created, idéalement avec l'adresse de la ressource créée."},
                {"type": "quiz", "id": "q2", "question": "Pourquoi `jsonify` plutôt que `json.dumps` ?", "choices": ["C'est identique", "Il pose le bon Content-Type et suit la configuration de l'application", "Il est plus rapide", "Il valide le schéma"], "answer": "Il pose le bon Content-Type et suit la configuration de l'application", "explanation": "`jsonify` renvoie une vraie réponse HTTP, étiquetée `application/json`."},
            ],
        },
        {
            "slug": "factory-et-blueprints",
            "title": "Fabrique d'application et blueprints",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Une application réelle ne crée pas son objet `Flask` au niveau du module. On passe par une **fabrique** (*application factory*) : une fonction qui construit l'application à partir d'une configuration. On peut ainsi créer une application de test différente de celle de production."},
                {"type": "code", "lang": "python", "code": '''# app/__init__.py
def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    from .api import auth
    app.register_blueprint(auth.bp)
    return app

# app/api/auth.py
bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@bp.post("/login")
def login():
    ...'''},
                {"type": "text", "md": "C'est exactement l'architecture de **cette** application : ouvrez `backend/app/__init__.py` et le dossier `backend/app/api/`."},
                {"type": "code", "lang": "python", "code": '''# tests/conftest.py : le client de test n'a pas besoin de serveur
import pytest
from app import create_app
from app.config import TestConfig

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()'''},
                {"type": "quiz", "id": "q1", "question": "À quoi sert une fabrique d'application ?", "choices": ["À aller plus vite", "À créer plusieurs applications avec des configurations différentes (test, production)", "Elle est obligatoire depuis Flask 3", "À se passer des blueprints"], "answer": "À créer plusieurs applications avec des configurations différentes (test, production)", "explanation": "Elle supprime l'état global et rend les tests indépendants les uns des autres."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-validation-payload",
            "title": "Valider les données d'une inscription",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Avant de toucher à la base, une vue doit valider ce qu'elle reçoit.

Écrivez `valider_inscription(data)`, qui renvoie un dictionnaire d'erreurs (vide si tout va bien) :

- `email` doit contenir un `@`, puis un `.` après ce `@` ; sinon `"Email invalide."`
- `username` doit faire au moins 3 caractères ; sinon `"3 caractères minimum."`
- `password` doit faire au moins 8 caractères ; sinon `"8 caractères minimum."`

Une clé absente doit produire la même erreur qu'une valeur vide.''',
            "starter_code": '''def valider_inscription(data):
    erreurs = {}
    ...
    return erreurs
''',
            "solution": '''def valider_inscription(data):
    erreurs = {}
    email = (data.get("email") or "").strip()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if "@" not in email or "." not in email.split("@")[-1]:
        erreurs["email"] = "Email invalide."
    if len(username) < 3:
        erreurs["username"] = "3 caractères minimum."
    if len(password) < 8:
        erreurs["password"] = "8 caractères minimum."
    return erreurs
''',
            "hints": [
                "`data.get(\"email\") or \"\"` traite d'un coup la clé absente et la valeur `None`.",
                "Pour le point après l'arobase : `email.split(\"@\")[-1]`.",
                "Quand tout est valide, renvoyez un dictionnaire vide, pas `None`.",
            ],
            "spec": {"tests": [
                {"name": "donnees_valides", "code": "assert valider_inscription({'email': 'a@b.fr', 'username': 'alice', 'password': 'motdepasse'}) == {}"},
                {"name": "email_invalide", "code": "e = valider_inscription({'email': 'abc', 'username': 'alice', 'password': 'motdepasse'})\nassert 'email' in e"},
                {"name": "cles_absentes", "code": "e = valider_inscription({})\nassert set(e) == {'email', 'username', 'password'}"},
                {"name": "mot_de_passe_court", "code": "e = valider_inscription({'email': 'a@b.fr', 'username': 'alice', 'password': 'court'})\nassert list(e) == ['password']"},
            ]},
        },
        {
            "slug": "tp-routeur",
            "title": "Un mini-routeur à la Flask",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Pour comprendre ce que fait Flask, écrivez un mini-routeur.

La classe `Routeur` expose :

- `route(chemin)` : un décorateur qui enregistre une vue. Le chemin peut contenir un paramètre entre chevrons, par exemple `/cours/<slug>` ;
- `dispatch(chemin)` : appelle la vue correspondante en lui passant la valeur capturée, et renvoie `(resultat, 200)` ;
- si aucune route ne correspond, `dispatch` renvoie `("Not Found", 404)`.

Un seul paramètre par chemin, et pas besoin d'expressions régulières.''',
            "starter_code": '''class Routeur:
    def __init__(self):
        self.routes = {}

    def route(self, chemin):
        def decorateur(fonction):
            ...
            return fonction
        return decorateur

    def dispatch(self, chemin):
        ...
''',
            "solution": '''class Routeur:
    def __init__(self):
        self.routes = {}

    def route(self, chemin):
        def decorateur(fonction):
            self.routes[chemin] = fonction
            return fonction
        return decorateur

    def dispatch(self, chemin):
        demande = [p for p in chemin.strip("/").split("/") if p != ""]
        for motif, vue in self.routes.items():
            parts = [p for p in motif.strip("/").split("/") if p != ""]
            if len(parts) != len(demande):
                continue
            params = []
            for attendu, recu in zip(parts, demande):
                if attendu.startswith("<") and attendu.endswith(">"):
                    params.append(recu)
                elif attendu != recu:
                    break
            else:
                return vue(*params), 200
        return "Not Found", 404
''',
            "hints": [
                "Depuis le décorateur, rangez `{chemin: fonction}` dans `self.routes`.",
                "Comparez les chemins segment par segment, après `strip('/').split('/')`.",
                "Un segment `<...>` accepte n'importe quelle valeur : mettez-la de côté.",
                "La clause `else` d'une boucle `for` s'exécute quand aucun `break` n'a eu lieu.",
            ],
            "spec": {"tests": [
                {"name": "route_statique", "code": "r = Routeur()\n@r.route('/sante')\ndef sante():\n    return 'ok'\nassert r.dispatch('/sante') == ('ok', 200)"},
                {"name": "route_parametree", "code": "r = Routeur()\n@r.route('/cours/<slug>')\ndef detail(slug):\n    return slug.upper()\nassert r.dispatch('/cours/flask') == ('FLASK', 200)"},
                {"name": "introuvable", "code": "r = Routeur()\nassert r.dispatch('/inconnu') == ('Not Found', 404)"},
                {"name": "longueur_differente", "code": "r = Routeur()\n@r.route('/cours/<slug>')\ndef detail(slug):\n    return slug\nassert r.dispatch('/cours') == ('Not Found', 404)"},
            ]},
        },
    ],
}
