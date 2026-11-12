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
                {"type": "quiz", "id": "q2", "question": "À quoi sert un blueprint ?", "choices": ["À dessiner l'interface", "À regrouper des routes par domaine, dans un module à part", "À chiffrer les sessions", "À remplacer la base de données"], "answer": "À regrouper des routes par domaine, dans un module à part", "explanation": "Chaque blueprint est ensuite enregistré dans la fabrique avec `app.register_blueprint`."},
                {"type": "quiz", "id": "q3", "question": "Pourquoi le client de test n'a-t-il pas besoin d'un serveur lancé ?", "choices": ["Il se connecte à la production", "Il appelle l'application directement, en mémoire", "Il simule un navigateur graphique", "Il lit les réponses dans un fichier"], "answer": "Il appelle l'application directement, en mémoire", "explanation": "Les tests sont rapides et ne dépendent d'aucun port réseau."},
            ],
        },
        {
            "slug": "base-de-donnees-et-authentification",
            "title": "Base de données, authentification et erreurs",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Flask ne fournit pas de base de données : on lui ajoute **SQLAlchemy**, un ORM. Une classe Python décrit une table, une instance décrit une ligne. Les modifications s'accumulent dans une **session**, et ne partent vers la base qu'au `commit`.'''},
                {"type": "code", "lang": "python", "code": '''from app.extensions import db


class Cours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    titre = db.Column(db.String(200), nullable=False)
    lecons = db.relationship("Lecon", backref="cours", cascade="all, delete-orphan")


# créer
cours = Cours(slug="flask", titre="Flask")
db.session.add(cours)
db.session.commit()

# lire
Cours.query.filter_by(slug="flask").first()
Cours.query.order_by(Cours.titre).all()

# en cas d'erreur, on annule tout ce qui était en attente
db.session.rollback()'''},
                {"type": "text", "md": '''Quand un modèle change, la base doit suivre. Une **migration** est un script versionné qui fait passer le schéma d'un état au suivant. Avec Flask-Migrate (Alembic) :

```bash
flask db migrate -m "ajout de la colonne niveau"   # génère le script
flask db upgrade                                   # l'applique
flask db downgrade                                 # revient en arrière
```

Relisez toujours le script généré : l'outil devine, il ne comprend pas. Un renommage de colonne, par exemple, est vu comme une suppression suivie d'un ajout — donc une perte de données.'''},
                {"type": "text", "md": '''**Authentification.** Deux règles ne se discutent pas :

1. on ne stocke **jamais** un mot de passe en clair, mais son **hachage** (argon2 ou bcrypt), impossible à inverser ;
2. le serveur ne fait confiance à rien de ce qui vient du client.

Une API sans état utilise souvent un **JWT** : à la connexion, le serveur signe un jeton qui contient l'identifiant de l'utilisateur et une date d'expiration. Le client le renvoie à chaque requête ; le serveur vérifie la signature, sans consulter de table de sessions.'''},
                {"type": "code", "lang": "python", "code": '''from flask_jwt_extended import create_access_token, current_user, jwt_required


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=data.get("email", "")).first()
    if user is None or not user.check_password(data.get("password", "")):
        # même message dans les deux cas : on ne révèle pas si le compte existe
        return jsonify({"error": "Identifiants invalides."}), 401
    return jsonify({"token": create_access_token(identity=str(user.id))})


@bp.get("/me")
@jwt_required()
def me():
    return jsonify({"user": current_user.to_dict()})'''},
                {"type": "callout", "tone": "warn", "md": "Un JWT est **signé**, pas chiffré : n'importe qui peut en lire le contenu. N'y mettez ni mot de passe ni donnée sensible, et donnez-lui une durée de vie courte."},
                {"type": "text", "md": '''**Erreurs.** Plutôt que de répéter des `try / except` dans chaque vue, on centralise : un gestionnaire transforme chaque erreur en réponse JSON cohérente. Le client reçoit toujours la même forme, et aucune trace d'exécution ne fuit vers l'extérieur.'''},
                {"type": "code", "lang": "python", "code": '''@app.errorhandler(404)
def introuvable(error):
    return jsonify({"error": "Ressource introuvable."}), 404


@app.errorhandler(Exception)
def erreur_interne(error):
    app.logger.exception("erreur non gérée")     # le détail reste dans les journaux
    db.session.rollback()
    return jsonify({"error": "Erreur interne."}), 500'''},
                {"type": "quiz", "id": "q1", "question": "Quand une modification SQLAlchemy est-elle écrite en base ?", "choices": ["Dès `db.session.add`", "Au `db.session.commit`", "À la création de l'objet", "À la fin de la requête HTTP, toujours"], "answer": "Au `db.session.commit`", "explanation": "Avant le commit, tout peut encore être annulé par un `rollback`."},
                {"type": "quiz", "id": "q2", "question": "Que stocke-t-on en base pour un mot de passe ?", "choices": ["Le mot de passe en clair", "Son hachage (argon2, bcrypt)", "Le mot de passe chiffré avec une clé du dépôt", "Rien"], "answer": "Son hachage (argon2, bcrypt)", "explanation": "Un hachage ne s'inverse pas : même une fuite de la base ne livre pas les mots de passe."},
                {"type": "quiz", "id": "q3", "question": "Peut-on mettre une donnée sensible dans un JWT ?", "choices": ["Oui, il est chiffré", "Non : il est signé, mais lisible par tous", "Oui, s'il expire vite", "Seulement en HTTPS"], "answer": "Non : il est signé, mais lisible par tous", "explanation": "La signature empêche de le modifier, pas de le lire."},
                {"type": "quiz", "id": "q4", "question": "Identifiants faux : pourquoi répondre le même message, que le compte existe ou non ?", "choices": ["Par paresse", "Pour ne pas révéler quels comptes existent", "Parce que Flask l'impose", "Pour accélérer la réponse"], "answer": "Pour ne pas révéler quels comptes existent", "explanation": "Un message distinct permettrait d'énumérer les adresses inscrites."},
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
        {
            "slug": "quiz-flask",
            "title": "Flask, les bons réflexes",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Codes HTTP, structure d'un projet et sécurité de base.",
            "spec": {"questions": [
                {"id": "1", "question": "Quel code HTTP quand l'utilisateur n'est pas authentifié ?", "choices": ["400", "401", "403", "404"], "answer": "401", "explanation": "401 : non authentifié. 403 : authentifié, mais pas autorisé."},
                {"id": "2", "question": "Quel code HTTP pour des données invalides envoyées par le client ?", "choices": ["200", "400", "500", "302"], "answer": "400", "explanation": "Les codes 4xx signalent une erreur du client, les 5xx une erreur du serveur."},
                {"id": "3", "question": "Quelle méthode HTTP pour supprimer une ressource ?", "choices": ["GET", "POST", "DELETE", "PATCH"], "answer": "DELETE", "explanation": "GET lit, POST crée, PUT et PATCH modifient, DELETE supprime."},
                {"id": "4", "question": "Comment récupérer le paramètre `page` de `/cours?page=2` ?", "choices": ["request.form[\"page\"]", "request.args.get(\"page\")", "request.get_json()[\"page\"]", "request.page"], "answer": "request.args.get(\"page\")", "explanation": "`request.args` contient les paramètres de l'URL, `request.form` ceux d'un formulaire."},
                {"id": "5", "question": "Quelle commande applique les migrations ?", "choices": ["flask db migrate", "flask db upgrade", "flask run", "flask db init"], "answer": "flask db upgrade", "explanation": "`migrate` génère le script, `upgrade` l'exécute."},
                {"id": "6", "question": "Où ranger SECRET_KEY ?", "choices": ["Dans le code", "Dans une variable d'environnement", "Dans le README", "Dans le frontend"], "answer": "Dans une variable d'environnement", "explanation": "Un secret ne va jamais dans le dépôt."},
                {"id": "7", "question": "Une vue lève une exception inattendue. Que doit recevoir le client ?", "choices": ["La trace d'exécution complète", "Un message générique et un code 500", "Un code 200 vide", "Le contenu du fichier de configuration"], "answer": "Un message générique et un code 500", "explanation": "Le détail va dans les journaux, pas chez le client."},
            ]},
        },
    ],
}
