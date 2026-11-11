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
    ],
}
