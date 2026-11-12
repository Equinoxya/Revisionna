COURSE = {
    "slug": "python",
    "title": "Python : les fondamentaux",
    "summary": "Types, structures de données, fonctions, compréhensions, objets et gestion des erreurs.",
    "category": "Langage",
    "level": "débutant",
    "icon": "Py",
    "lessons": [
        {
            "slug": "types-et-structures",
            "title": "Types et structures de données",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": '''Python est **dynamiquement typé** : une variable est une étiquette posée sur un objet. C'est l'objet qui porte le type, pas la variable.

Les quatre structures à maîtriser :

| Structure | Modifiable | Ordonnée | Usage typique |
|---|---|---|---|
| `list` | oui | oui | séquence que l'on fait évoluer |
| `tuple` | non | oui | enregistrement figé, clé de dictionnaire |
| `dict` | oui | oui (ordre d'insertion) | association clé → valeur |
| `set` | oui | non | unicité, opérations ensemblistes |'''},
                {"type": "code", "lang": "python", "code": '''notes = {"alice": 14, "bob": 9}
notes["chloe"] = 17          # ajout
moyenne = sum(notes.values()) / len(notes)
print(f"moyenne = {moyenne:.2f}")

admis = {nom for nom, note in notes.items() if note >= 10}
print(admis)                 # {'alice', 'chloe'}'''},
                {"type": "callout", "tone": "warn", "md": "Piège classique : ne jamais donner une liste comme valeur par défaut d'un paramètre (`def f(x=[])`). Elle est créée **une seule fois**, à la définition de la fonction, puis partagée par tous les appels."},
                {"type": "quiz", "id": "q1", "question": "Quel type choisir pour servir de clé de dictionnaire ?", "choices": ["list", "tuple", "set", "dict"], "answer": "tuple", "explanation": "Une clé doit être hachable, donc immuable : le tuple l'est, la liste non."},
                {"type": "quiz", "id": "q2", "question": "Que vaut `len({1, 2, 2, 3})` ?", "choices": ["2", "3", "4", "Une erreur"], "answer": "3", "explanation": "Un ensemble élimine les doublons : il reste {1, 2, 3}."},
            ],
        },
        {
            "slug": "fonctions-et-comprehensions",
            "title": "Fonctions, compréhensions, générateurs",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": '''Une **compréhension** remplace une boucle `for` suivie d'un `append`. Elle est plus courte et plus rapide.

Un **générateur** (des parenthèses au lieu des crochets) produit les valeurs à la demande : la mémoire utilisée reste constante, même sur un flux infini.'''},
                {"type": "code", "lang": "python", "code": '''carres = [n * n for n in range(10) if n % 2 == 0]
print(carres)                      # [0, 4, 16, 36, 64]

# générateur : rien n'est calculé avant l'itération
flux = (n * n for n in range(10_000_000))
print(next(flux), next(flux))      # 0 1

def compteur(debut=0):
    """Générateur infini avec yield."""
    while True:
        yield debut
        debut += 1'''},
                {"type": "text", "md": "Côté arguments : `*args` capture les arguments positionnels, `**kwargs` les arguments nommés. Quand vous connaissez les paramètres, nommez-les explicitement."},
                {"type": "quiz", "id": "q1", "question": "Quelle différence entre `[x for x in it]` et `(x for x in it)` ?", "choices": ["Aucune", "La seconde est un générateur paresseux", "La seconde est un tuple", "La seconde est plus lente"], "answer": "La seconde est un générateur paresseux", "explanation": "Les parenthèses créent un générateur : chaque valeur est calculée au moment où on la demande."},
            ],
        },
        {
            "slug": "poo-et-exceptions",
            "title": "Objets et gestion des erreurs",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Une classe regroupe un état (les attributs) et un comportement (les méthodes). `__init__` initialise l'instance, `__repr__` sert au débogage, et une `@property` expose un calcul comme s'il s'agissait d'un attribut."},
                {"type": "code", "lang": "python", "code": '''class Etudiant:
    def __init__(self, nom, notes=None):
        self.nom = nom
        self.notes = list(notes or [])

    @property
    def moyenne(self):
        if not self.notes:
            return 0.0
        return sum(self.notes) / len(self.notes)

    def __repr__(self):
        return f"Etudiant({self.nom!r}, moyenne={self.moyenne:.1f})"

print(Etudiant("Alice", [12, 16]))'''},
                {"type": "text", "md": "Côté erreurs : attrapez **l'exception précise**, jamais un `except:` nu. Pour vos erreurs métier, créez vos propres exceptions en héritant de `Exception`."},
                {"type": "code", "lang": "python", "code": '''class NoteInvalide(ValueError):
    pass

def ajouter(etudiant, note):
    if not 0 <= note <= 20:
        raise NoteInvalide(f"note hors bornes : {note}")
    etudiant.notes.append(note)'''},
                {"type": "quiz", "id": "q1", "question": "Pourquoi éviter `except Exception: pass` ?", "choices": ["C'est plus lent", "Cela masque les vrais bugs", "Python l'interdit", "Cela consomme de la mémoire"], "answer": "Cela masque les vrais bugs", "explanation": "Vous avalez aussi les erreurs que vous n'aviez pas prévues : le bug devient invisible."},
                {"type": "quiz", "id": "q2", "question": "Que désigne `self` dans une méthode ?", "choices": ["La classe", "L'instance sur laquelle la méthode est appelée", "Le module", "Le parent de la classe"], "answer": "L'instance sur laquelle la méthode est appelée", "explanation": "`e.moyenne()` revient à `Etudiant.moyenne(e)` : Python passe l'instance en premier argument."},
                {"type": "quiz", "id": "q3", "question": "Dans try / except / finally, quand le bloc finally s'exécute-t-il ?", "choices": ["Seulement s'il y a une erreur", "Seulement s'il n'y en a pas", "Toujours", "Jamais si except attrape l'erreur"], "answer": "Toujours", "explanation": "C'est l'endroit où libérer une ressource, erreur ou non."},
            ],
        },
        {
            "slug": "fichiers-modules-et-environnement",
            "title": "Fichiers, modules et environnement virtuel",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Un programme utile lit et écrit des **fichiers**. On les ouvre toujours avec `with` : le fichier est refermé à la sortie du bloc, même si une erreur survient. Précisez l'encodage : sans lui, Python prend celui du système, et vos accents se cassent d'une machine à l'autre.'''},
                {"type": "code", "lang": "python", "code": '''import json
from pathlib import Path

dossier = Path("donnees")
dossier.mkdir(exist_ok=True)
fichier = dossier / "notes.json"          # / assemble les chemins

# écrire
with fichier.open("w", encoding="utf-8") as f:
    json.dump({"alice": 14, "bob": 9}, f, ensure_ascii=False, indent=2)

# lire
with fichier.open(encoding="utf-8") as f:
    notes = json.load(f)

# parcourir un fichier texte ligne par ligne, sans tout charger en mémoire
with open("journal.log", encoding="utf-8") as f:
    erreurs = [ligne.strip() for ligne in f if "ERROR" in ligne]'''},
                {"type": "text", "md": '''Les modes d'ouverture : `"r"` lecture (par défaut), `"w"` écriture **en écrasant**, `"a"` ajout à la fin, `"b"` binaire (images, archives).

`pathlib.Path` remplace avantageusement les chaînes de caractères : `chemin.exists()`, `chemin.suffix`, `chemin.read_text()`, `chemin.glob("*.py")`.'''},
                {"type": "text", "md": '''Dès qu'un fichier dépasse quelques centaines de lignes, on le découpe en **modules**. Un module est simplement un fichier `.py` ; un **paquet** est un dossier de modules.

```python
import math                        # tout le module : math.sqrt(2)
from statistics import mean        # un seul nom
from app.services import ai        # un module d'un paquet
```

Un module est exécuté **une seule fois**, à son premier import. Pour qu'un fichier serve à la fois de module et de script, on protège le code à lancer :'''},
                {"type": "code", "lang": "python", "code": '''# outils.py
def moyenne(notes):
    return sum(notes) / len(notes)


if __name__ == "__main__":
    # exécuté avec « python outils.py », ignoré lors d'un « import outils »
    print(moyenne([12, 15, 9]))'''},
                {"type": "text", "md": '''Chaque projet a ses dépendances, dans ses versions. Un **environnement virtuel** les isole : ce que vous installez pour un projet ne casse pas les autres.'''},
                {"type": "code", "lang": "bash", "code": '''python3 -m venv .venv              # créer l'environnement
source .venv/bin/activate          # l'activer (Windows : .venv\\Scripts\\activate)
pip install flask                  # installer dans l'environnement
pip freeze > requirements.txt      # figer les versions
pip install -r requirements.txt    # reproduire ailleurs'''},
                {"type": "callout", "tone": "warn", "md": "Le dossier `.venv` ne se partage pas : il va dans `.gitignore`. Ce qu'on met dans le dépôt, c'est `requirements.txt`, qui permet de le reconstruire."},
                {"type": "text", "md": '''Les **annotations de type** documentent ce qu'une fonction attend et renvoie. Python ne les vérifie pas à l'exécution, mais votre éditeur et des outils comme `mypy` s'en servent pour repérer les erreurs avant le lancement.

```python
def moyenne(notes: list[float]) -> float:
    return sum(notes) / len(notes)

def chercher(nom: str, annuaire: dict[str, int]) -> int | None:
    return annuaire.get(nom)
```'''},
                {"type": "quiz", "id": "q1", "question": "Pourquoi ouvrir un fichier avec `with` ?", "choices": ["C'est plus rapide", "Le fichier est refermé automatiquement, même en cas d'erreur", "C'est obligatoire pour lire", "Pour le chiffrer"], "answer": "Le fichier est refermé automatiquement, même en cas d'erreur", "explanation": "`with` garantit la libération de la ressource."},
                {"type": "quiz", "id": "q2", "question": "Que fait le mode d'ouverture \"w\" sur un fichier existant ?", "choices": ["Il ajoute à la fin", "Il écrase le contenu", "Il lève une erreur", "Il ouvre en lecture"], "answer": "Il écrase le contenu", "explanation": "Pour ajouter sans effacer, c'est le mode \"a\"."},
                {"type": "quiz", "id": "q3", "question": "À quoi sert un environnement virtuel ?", "choices": ["À accélérer Python", "À isoler les dépendances de chaque projet", "À chiffrer le code", "À exécuter du code sans Python"], "answer": "À isoler les dépendances de chaque projet", "explanation": "Deux projets peuvent ainsi utiliser deux versions différentes de la même bibliothèque."},
                {"type": "quiz", "id": "q4", "question": "Quand le bloc `if __name__ == \"__main__\":` s'exécute-t-il ?", "choices": ["À chaque import", "Quand le fichier est lancé directement", "Jamais", "Seulement dans les tests"], "answer": "Quand le fichier est lancé directement", "explanation": "À l'import, `__name__` vaut le nom du module, pas `__main__`."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-statistiques",
            "title": "Statistiques sur une liste de notes",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Écrivez trois fonctions :

1. `moyenne(notes)` renvoie la moyenne, et `0.0` si la liste est vide.
2. `admis(notes, seuil=10)` renvoie la liste des notes supérieures ou égales au seuil.
3. `repartition(notes)` renvoie un dictionnaire `{"faible": n, "moyen": n, "bon": n}`, avec `faible < 8 <= moyen < 14 <= bon`.

Aucun import n'est nécessaire.''',
            "starter_code": '''def moyenne(notes):
    ...


def admis(notes, seuil=10):
    ...


def repartition(notes):
    ...
''',
            "solution": '''def moyenne(notes):
    return sum(notes) / len(notes) if notes else 0.0


def admis(notes, seuil=10):
    return [n for n in notes if n >= seuil]


def repartition(notes):
    buckets = {"faible": 0, "moyen": 0, "bon": 0}
    for note in notes:
        if note < 8:
            buckets["faible"] += 1
        elif note < 14:
            buckets["moyen"] += 1
        else:
            buckets["bon"] += 1
    return buckets
''',
            "hints": [
                "Pour la liste vide, testez `if not notes` avant la division.",
                "`admis` tient en une compréhension de liste.",
                "Pour `repartition`, initialisez les trois clés à 0, puis incrémentez.",
            ],
            "spec": {"tests": [
                {"name": "moyenne_simple", "code": "assert abs(moyenne([10, 20]) - 15) < 1e-9"},
                {"name": "moyenne_vide", "code": "assert moyenne([]) == 0.0"},
                {"name": "admis_defaut", "code": "assert admis([5, 10, 15]) == [10, 15]"},
                {"name": "admis_seuil", "code": "assert admis([5, 10, 15], seuil=12) == [15]"},
                {"name": "repartition", "code": "assert repartition([4, 9, 18]) == {'faible': 1, 'moyen': 1, 'bon': 1}"},
                {"name": "repartition_bornes", "code": "assert repartition([8, 14]) == {'faible': 0, 'moyen': 1, 'bon': 1}"},
            ]},
        },
        {
            "slug": "tp-classe-panier",
            "title": "Une classe Panier",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Implémentez la classe `Panier` :

- `ajouter(nom, prix, quantite=1)` cumule les quantités si l'article existe déjà ;
- `retirer(nom)` supprime l'article, et lève `KeyError` s'il est absent ;
- la propriété `total` renvoie la somme des `prix * quantite` ;
- `__len__` renvoie le nombre d'articles distincts ;
- un prix négatif lève `ValueError`.''',
            "starter_code": '''class Panier:
    def __init__(self):
        self.articles = {}

    def ajouter(self, nom, prix, quantite=1):
        ...

    def retirer(self, nom):
        ...

    @property
    def total(self):
        ...

    def __len__(self):
        ...
''',
            "solution": '''class Panier:
    def __init__(self):
        self.articles = {}

    def ajouter(self, nom, prix, quantite=1):
        if prix < 0:
            raise ValueError("prix négatif")
        existant = self.articles.get(nom)
        if existant:
            existant["quantite"] += quantite
        else:
            self.articles[nom] = {"prix": prix, "quantite": quantite}

    def retirer(self, nom):
        del self.articles[nom]

    @property
    def total(self):
        return sum(a["prix"] * a["quantite"] for a in self.articles.values())

    def __len__(self):
        return len(self.articles)
''',
            "hints": [
                "Stockez un dictionnaire `{nom: {\"prix\": ..., \"quantite\": ...}}`.",
                "`del self.articles[nom]` lève déjà `KeyError` : laissez-la remonter.",
                "`total` est une somme sur `self.articles.values()`.",
            ],
            "spec": {"tests": [
                {"name": "ajout_et_total", "code": "p = Panier()\np.ajouter('thé', 3.5, 2)\nassert abs(p.total - 7.0) < 1e-9"},
                {"name": "cumul_quantite", "code": "p = Panier()\np.ajouter('thé', 3.0)\np.ajouter('thé', 3.0, 2)\nassert len(p) == 1 and abs(p.total - 9.0) < 1e-9"},
                {"name": "retirer", "code": "p = Panier()\np.ajouter('thé', 3.0)\np.retirer('thé')\nassert len(p) == 0"},
                {"name": "retirer_absent", "code": "p = Panier()\ntry:\n    p.retirer('café')\nexcept KeyError:\n    pass\nelse:\n    raise AssertionError('KeyError attendue')"},
                {"name": "prix_negatif", "code": "p = Panier()\ntry:\n    p.ajouter('thé', -1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('ValueError attendue')"},
            ]},
        },
        {
            "slug": "tp-comptage-mots",
            "title": "Compter les mots d'un texte",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Écrivez `mots_frequents(texte, n=3)`, qui renvoie les `n` mots les plus fréquents d'un texte, sous la forme d'une liste de couples `(mot, nombre)`.

- la casse est ignorée : `Python` et `python` sont le même mot ;
- la ponctuation `. , ; : ! ?` est retirée ;
- les plus fréquents d'abord ; à égalité, par ordre alphabétique.

```python
mots_frequents("Le chat. Le chien, le chat !", 2)  # [("le", 3), ("chat", 2)]
```''',
            "starter_code": '''def mots_frequents(texte, n=3):
    ...
''',
            "solution": '''def mots_frequents(texte, n=3):
    for signe in ".,;:!?":
        texte = texte.replace(signe, " ")

    compte = {}
    for mot in texte.lower().split():
        compte[mot] = compte.get(mot, 0) + 1

    classement = sorted(compte.items(), key=lambda couple: (-couple[1], couple[0]))
    return classement[:n]
''',
            "hints": [
                "Remplacez chaque signe de ponctuation par une espace, puis utilisez `split()`.",
                "Un dictionnaire `{mot: nombre}` fait le comptage : `compte.get(mot, 0) + 1`.",
                "Triez `compte.items()` avec la clé `(-nombre, mot)`.",
            ],
            "spec": {"tests": [
                {"name": "exemple", "code": "assert mots_frequents('Le chat. Le chien, le chat !', 2) == [('le', 3), ('chat', 2)]"},
                {"name": "casse_ignoree", "code": "assert mots_frequents('Python python PYTHON', 1) == [('python', 3)]"},
                {"name": "egalite_alphabetique", "code": "assert mots_frequents('b a c', 3) == [('a', 1), ('b', 1), ('c', 1)]"},
                {"name": "n_par_defaut", "code": "assert len(mots_frequents('a b c d e')) == 3"},
                {"name": "texte_vide", "code": "assert mots_frequents('') == []"},
            ]},
        },
        {
            "slug": "quiz-python",
            "title": "Python sans hésiter",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Les réflexes à avoir sur les bases du langage.",
            "spec": {"questions": [
                {"id": "1", "question": "Que vaut `[1, 2, 3][-1]` ?", "choices": ["1", "3", "Une erreur", "[3]"], "answer": "3", "explanation": "Un indice négatif compte depuis la fin."},
                {"id": "2", "question": "Quelle structure garantit l'unicité de ses éléments ?", "choices": ["list", "tuple", "set", "str"], "answer": "set", "explanation": "Un ensemble ne contient jamais deux fois la même valeur."},
                {"id": "3", "question": "Que renvoie `{\"a\": 1}.get(\"b\", 0)` ?", "choices": ["None", "0", "Une KeyError", "1"], "answer": "0", "explanation": "`get` renvoie la valeur par défaut quand la clé manque, sans lever d'erreur."},
                {"id": "4", "question": "Un tuple est-il modifiable ?", "choices": ["Oui", "Non, il est immuable", "Seulement s'il est vide", "Seulement avec append"], "answer": "Non, il est immuable", "explanation": "C'est ce qui lui permet de servir de clé de dictionnaire."},
                {"id": "5", "question": "Que vaut `\"a,b,c\".split(\",\")` ?", "choices": ["\"abc\"", "[\"a\", \"b\", \"c\"]", "(\"a\", \"b\", \"c\")", "3"], "answer": "[\"a\", \"b\", \"c\"]", "explanation": "`split` découpe une chaîne en liste ; `\",\".join(...)` fait l'inverse."},
                {"id": "6", "question": "Quelle différence entre `==` et `is` ?", "choices": ["Aucune", "== compare les valeurs, is compare l'identité des objets", "is compare les valeurs", "== ne fonctionne que sur les nombres"], "answer": "== compare les valeurs, is compare l'identité des objets", "explanation": "On réserve `is` à `None` : `if x is None`."},
                {"id": "7", "question": "Quel fichier liste les dépendances d'un projet Python ?", "choices": ["package.json", "requirements.txt", "Dockerfile", ".gitignore"], "answer": "requirements.txt", "explanation": "On l'installe avec `pip install -r requirements.txt`."},
                {"id": "8", "question": "Que produit `range(2, 8, 2)` ?", "choices": ["2, 4, 6", "2, 4, 6, 8", "2, 8", "0, 2, 4, 6"], "answer": "2, 4, 6", "explanation": "La borne de fin est exclue."},
            ]},
        },
    ],
}
