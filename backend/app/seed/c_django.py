COURSE = {
    "slug": "django",
    "title": "Django : framework complet",
    "summary": "Architecture MTV, ORM, migrations, interface d'administration, API REST, et ce qui le distingue de Flask.",
    "category": "Backend",
    "level": "intermédiaire",
    "icon": "Dj",
    "lessons": [
        {
            "slug": "mtv-et-orm",
            "title": "Architecture MTV et ORM",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Django suit le découpage **MTV** : *Model* (les données), *Template* (le rendu), *View* (la logique). Le routeur (`urls.py`) relie une URL à une vue.

Contrairement à Flask, Django fournit tout : ORM, migrations, interface d'administration, authentification, formulaires. On parle d'un framework « piles incluses ».'''},
                {"type": "code", "lang": "python", "code": '''# cours/models.py
from django.db import models

class Cours(models.Model):
    slug = models.SlugField(unique=True)
    titre = models.CharField(max_length=160)
    publie = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["titre"]

    def __str__(self):
        return self.titre

class Lecon(models.Model):
    cours = models.ForeignKey(Cours, related_name="lecons", on_delete=models.CASCADE)
    titre = models.CharField(max_length=160)
    ordre = models.PositiveIntegerField(default=0)'''},
                {"type": "text", "md": "L'ORM écrit le SQL à votre place. Les requêtes sont **paresseuses** : rien ne part vers la base avant qu'on parcoure le résultat."},
                {"type": "code", "lang": "python", "code": '''Cours.objects.filter(publie=True).count()
Cours.objects.filter(titre__icontains="python")

# problème N+1 : une requête par cours pour lire ses leçons
for c in Cours.objects.all():
    print(c.lecons.count())

# corrigé : 2 requêtes au total
for c in Cours.objects.prefetch_related("lecons"):
    print(len(c.lecons.all()))'''},
                {"type": "callout", "tone": "warn", "md": "`select_related` pour les relations **ForeignKey et OneToOne** (une jointure SQL), `prefetch_related` pour les relations **inverses et ManyToMany** (une seconde requête)."},
                {"type": "quiz", "id": "q1", "question": "Que fait `python manage.py makemigrations` ?", "choices": ["Il applique les migrations à la base", "Il génère les fichiers de migration à partir des modèles", "Il crée la base de données", "Il lance le serveur"], "answer": "Il génère les fichiers de migration à partir des modèles", "explanation": "C'est `migrate` qui les applique ensuite à la base."},
                {"type": "quiz", "id": "q2", "question": "Quel outil contre le problème N+1 sur une ForeignKey ?", "choices": ["prefetch_related", "select_related", "annotate", "values_list"], "answer": "select_related", "explanation": "`select_related` fait une jointure SQL : une seule requête."},
            ],
        },
        {
            "slug": "drf-et-admin",
            "title": "Administration et API REST",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": "L'**interface d'administration** de Django est générée à partir des modèles : quelques lignes suffisent pour obtenir un back-office complet."},
                {"type": "code", "lang": "python", "code": '''# cours/admin.py
from django.contrib import admin
from .models import Cours

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ("titre", "slug", "publie")
    list_filter = ("publie",)
    search_fields = ("titre",)'''},
                {"type": "text", "md": "Pour une API JSON, on ajoute **Django REST Framework** : un *serializer* valide et convertit les données, un *ViewSet* expose les opérations de lecture et d'écriture."},
                {"type": "code", "lang": "python", "code": '''class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = ["id", "slug", "titre", "publie"]

class CoursViewSet(viewsets.ModelViewSet):
    queryset = Cours.objects.all()
    serializer_class = CoursSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]'''},
                {"type": "text", "md": "**Flask ou Django ?** Flask pour une petite API dont on veut choisir chaque brique ; Django quand on veut l'administration, l'authentification et les migrations prêtes à l'emploi."},
                {"type": "quiz", "id": "q1", "question": "Quel est le rôle d'un serializer ?", "choices": ["Produire du HTML", "Valider les entrées et convertir entre modèle et JSON", "Gérer les migrations", "Router les URL"], "answer": "Valider les entrées et convertir entre modèle et JSON", "explanation": "C'est l'équivalent du formulaire, côté API."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-queryset-simule",
            "title": "Simuler un QuerySet paresseux",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Les QuerySet de Django s'enchaînent, et ne font rien tant qu'on ne leur demande pas de résultat. Reproduisez ce principe.

`QuerySet(donnees)` reçoit une liste de dictionnaires :

- `filter(**criteres)` renvoie un **nouveau** QuerySet (égalité stricte sur chaque critère), sans rien évaluer ;
- `order_by(cle)` trie ; un `-` devant la clé inverse l'ordre ;
- `count()` renvoie le nombre d'éléments ;
- `all()` renvoie la liste des éléments ;
- `self.requetes` compte les évaluations réelles : il augmente de 1 à chaque appel de `count()` ou de `all()`, jamais lors d'un `filter` ou d'un `order_by`.''',
            "starter_code": '''class QuerySet:
    def __init__(self, donnees):
        self.donnees = list(donnees)
        self.requetes = 0

    def filter(self, **criteres):
        ...

    def order_by(self, cle):
        ...

    def count(self):
        ...

    def all(self):
        ...
''',
            "solution": '''class QuerySet:
    def __init__(self, donnees):
        self.donnees = list(donnees)
        self.requetes = 0

    def filter(self, **criteres):
        resultat = [
            item for item in self.donnees
            if all(item.get(cle) == valeur for cle, valeur in criteres.items())
        ]
        return QuerySet(resultat)

    def order_by(self, cle):
        decroissant = cle.startswith("-")
        champ = cle[1:] if decroissant else cle
        return QuerySet(sorted(self.donnees, key=lambda item: item[champ], reverse=decroissant))

    def count(self):
        self.requetes += 1
        return len(self.donnees)

    def all(self):
        self.requetes += 1
        return list(self.donnees)
''',
            "hints": [
                "`filter` et `order_by` doivent renvoyer `QuerySet(nouvelle_liste)`, pas `self`.",
                "`all(... for ...)` vérifie tous les critères d'un coup.",
                "Seuls `count()` et `all()` font augmenter `self.requetes`.",
            ],
            "spec": {"tests": [
                {"name": "filter_simple", "code": "qs = QuerySet([{'t': 'a', 'p': True}, {'t': 'b', 'p': False}])\nassert qs.filter(p=True).count() == 1"},
                {"name": "paresseux", "code": "qs = QuerySet([{'t': 'a'}])\nqs.filter(t='a').order_by('t')\nassert qs.requetes == 0"},
                {"name": "evaluation_comptee", "code": "qs = QuerySet([{'t': 'a'}])\nqs.all()\nqs.count()\nassert qs.requetes == 2"},
                {"name": "ordre_decroissant", "code": "qs = QuerySet([{'n': 1}, {'n': 3}, {'n': 2}])\nassert [d['n'] for d in qs.order_by('-n').all()] == [3, 2, 1]"},
                {"name": "enchainement", "code": "qs = QuerySet([{'t': 'a', 'p': True}, {'t': 'c', 'p': True}, {'t': 'b', 'p': False}])\nassert [d['t'] for d in qs.filter(p=True).order_by('t').all()] == ['a', 'c']"},
            ]},
        },
        {
            "slug": "quiz-django",
            "title": "Les réflexes Django",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Cinq questions sur la vie d'un projet Django.",
            "spec": {"questions": [
                {"id": "1", "question": "Quelle commande applique les migrations à la base ?", "choices": ["manage.py makemigrations", "manage.py migrate", "manage.py runserver", "manage.py shell"], "answer": "manage.py migrate", "explanation": "`makemigrations` génère les fichiers, `migrate` les applique."},
                {"id": "2", "question": "Où déclare-t-on les routes d'un projet ?", "choices": ["models.py", "urls.py", "settings.py", "apps.py"], "answer": "urls.py", "explanation": "Dans la liste `urlpatterns` de `urls.py`, souvent découpée par application."},
                {"id": "3", "question": "Que signifie `on_delete=models.CASCADE` ?", "choices": ["La suppression est interdite", "Les objets liés sont supprimés aussi", "La clé passe à NULL", "L'objet est archivé"], "answer": "Les objets liés sont supprimés aussi", "explanation": "`PROTECT` interdit la suppression, `SET_NULL` vide la clé."},
                {"id": "4", "question": "Quel réglage ne doit JAMAIS valoir True en production ?", "choices": ["USE_TZ", "DEBUG", "ALLOWED_HOSTS", "USE_I18N"], "answer": "DEBUG", "explanation": "`DEBUG=True` expose la configuration et le détail des erreurs."},
                {"id": "5", "question": "Comment compter sans charger les objets en mémoire ?", "choices": ["len(qs.all())", "qs.count()", "list(qs)", "qs[:]"], "answer": "qs.count()", "explanation": "`count()` délègue un `SELECT COUNT(*)` à la base."},
            ]},
        },
    ],
}
