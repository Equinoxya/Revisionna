COURSE = {
    "slug": "nosql",
    "title": "NoSQL : MongoDB et au-delà",
    "summary": "Modèles document et clé-valeur, choix entre SQL et NoSQL, agrégations MongoDB.",
    "category": "Données",
    "level": "intermédiaire",
    "icon": "No",
    "lessons": [
        {
            "slug": "familles-nosql",
            "title": "Les familles NoSQL, et quand les choisir",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": '''NoSQL ne veut pas dire « contre SQL », mais *not only SQL*. On distingue quatre familles :

| Famille | Exemple | Bien adaptée à |
|---|---|---|
| Document | MongoDB | objets imbriqués, structure qui évolue |
| Clé-valeur | Redis | cache, sessions, compteurs |
| Colonnes | Cassandra | très gros volumes en écriture |
| Graphe | Neo4j | relations profondes, recommandations |'''},
                {"type": "text", "md": "**Théorème CAP** : quand le réseau se coupe entre deux serveurs, il faut choisir entre cohérence et disponibilité. PostgreSQL privilégie la cohérence, un cluster Cassandra la disponibilité."},
                {"type": "callout", "tone": "warn", "md": "NoSQL n'est pas « plus simple ». L'absence de schéma déplace la validation dans le code de l'application : sans discipline, on se retrouve avec des documents incohérents."},
                {"type": "quiz", "id": "q1", "question": "Vous stockez des sessions utilisateur qui expirent. Que choisir ?", "choices": ["Une base graphe", "Une base clé-valeur (Redis)", "Une base en colonnes", "Une base document"], "answer": "Une base clé-valeur (Redis)", "explanation": "Accès par clé, expiration intégrée, tout en mémoire : c'est l'usage type du clé-valeur."},
                {"type": "quiz", "id": "q2", "question": "Quand rester sur du relationnel ?", "choices": ["Jamais", "Quand les données sont très liées et que les transactions sont critiques", "Seulement pour les petites bases", "Quand on utilise Python"], "answer": "Quand les données sont très liées et que les transactions sont critiques", "explanation": "Jointures, contraintes d'intégrité et transactions restent les points forts du relationnel."},
            ],
        },
        {
            "slug": "mongodb-pratique",
            "title": "MongoDB : requêtes et agrégations",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Un document MongoDB ressemble à un dictionnaire Python. On interroge une collection avec `find`, et on transforme les données avec un **pipeline d'agrégation**."},
                {"type": "code", "lang": "python", "code": '''from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017")["revisionna"]

db.activity.insert_one({
    "event": "exercise_submitted",
    "user_id": 1,
    "exercise": "tp-statistiques",
    "passed": True,
})

# toutes les réussites d'un utilisateur, les plus récentes d'abord
list(db.activity.find({"user_id": 1, "passed": True}).sort("at", -1).limit(10))'''},
                {"type": "code", "lang": "python", "code": '''# nombre de tentatives et de réussites par exercice
pipeline = [
    {"$match": {"event": "exercise_submitted"}},
    {"$group": {
        "_id": "$exercise",
        "tentatives": {"$sum": 1},
        "reussies": {"$sum": {"$cond": ["$passed", 1, 0]}},
    }},
    {"$sort": {"tentatives": -1}},
]
list(db.activity.aggregate(pipeline))'''},
                {"type": "text", "md": "Dans cette application, c'est `backend/app/services/activity.py` qui tient ce journal. Si `MONGO_URL` est vide, l'écriture est simplement ignorée : une dépendance facultative ne doit jamais faire tomber l'API. Et comme ces documents concernent des personnes, un index TTL les efface automatiquement au bout de quelques mois."},
                {"type": "quiz", "id": "q1", "question": "Quel est l'équivalent MongoDB du `GROUP BY` ?", "choices": ["$match", "$group", "$project", "$lookup"], "answer": "$group", "explanation": "`$match` correspond à WHERE, `$group` à GROUP BY, `$lookup` à JOIN, `$project` à SELECT."},
                {"type": "quiz", "id": "q2", "question": "Dans un pipeline, pourquoi placer `$match` le plus tôt possible ?", "choices": ["C'est obligatoire", "Pour réduire le nombre de documents traités par les étapes suivantes", "Pour trier", "Pour renommer les champs"], "answer": "Pour réduire le nombre de documents traités par les étapes suivantes", "explanation": "Filtrer d'abord permet aussi d'utiliser un index."},
                {"type": "quiz", "id": "q3", "question": "Que renvoie `find_one` quand rien ne correspond ?", "choices": ["Une erreur", "None", "Un document vide", "Une liste vide"], "answer": "None", "explanation": "Il faut donc tester le résultat avant de s'en servir."},
            ],
        },
        {
            "slug": "modelisation-et-redis",
            "title": "Modéliser des documents, et Redis en cache",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''En relationnel, on modélise les **données** puis on écrit les requêtes. En document, on fait l'inverse : on part des **requêtes** que l'application fera le plus souvent, et on range les données pour qu'elles soient lues d'un seul coup.

Deux façons de relier des informations :

| | Imbriquer (*embed*) | Référencer |
|---|---|---|
| Principe | le sous-document vit dans le parent | on stocke l'identifiant |
| Lecture | une seule requête | plusieurs requêtes, ou `$lookup` |
| Mise à jour | à refaire dans chaque copie | à un seul endroit |
| Pour | ce qui se lit ensemble et change peu | ce qui est partagé ou volumineux |'''},
                {"type": "code", "lang": "python", "code": '''# imbriqué : les leçons n'existent pas sans leur cours
{
    "_id": "flask",
    "titre": "Flask",
    "lecons": [
        {"slug": "routes", "titre": "Routes", "duree": 15},
        {"slug": "factory", "titre": "Fabrique", "duree": 20},
    ],
}

# référencé : un étudiant est partagé entre beaucoup de tentatives
{"_id": 4812, "etudiant_id": 17, "exercice": "tp-routeur", "reussi": True}'''},
                {"type": "callout", "tone": "warn", "md": "Un document MongoDB est limité à **16 Mo**. Un tableau qui grossit sans fin (les commentaires d'un article, les événements d'un compte) finit par poser problème : on le sort dans sa propre collection."},
                {"type": "text", "md": '''Comme en SQL, une recherche sans **index** parcourt toute la collection. On indexe les champs sur lesquels on filtre et on trie, et on vérifie avec `explain()`.

```python
db.tentatives.create_index([("etudiant_id", 1), ("date", -1)])
db.sessions.create_index("expire_le", expireAfterSeconds=0)   # index TTL : purge automatique
```'''},
                {"type": "text", "md": '''**Redis** est une base **clé-valeur en mémoire** : des lectures et des écritures en moins d'une milliseconde. Son usage le plus courant est le **cache** : on garde le résultat d'un calcul coûteux pendant un certain temps, pour ne pas le refaire à chaque requête.'''},
                {"type": "code", "lang": "python", "code": '''import json
import redis

r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)


def catalogue():
    en_cache = r.get("catalogue")
    if en_cache is not None:                 # trouvé : pas de requête SQL
        return json.loads(en_cache)

    cours = charger_depuis_la_base()         # absent : on calcule…
    r.set("catalogue", json.dumps(cours), ex=300)   # …et on garde 5 minutes
    return cours


r.incr("visites:accueil")                    # compteur atomique
r.delete("catalogue")                        # invalider après une modification'''},
                {"type": "text", "md": '''Ce schéma s'appelle *cache-aside*. Deux questions se posent toujours :

- **combien de temps** garder la valeur ? C'est le **TTL** (`ex=300`) : au-delà, la clé disparaît d'elle-même ;
- **quand l'invalider** ? Dès que la donnée d'origine change, on supprime la clé.

Redis sert aussi aux sessions, aux compteurs, à la limitation de débit et aux files d'attente. Comme tout vit en mémoire, on n'y range que des données qu'on sait **reconstruire** : la source de vérité reste la base principale.'''},
                {"type": "quiz", "id": "q1", "question": "Quand imbriquer un sous-document plutôt que le référencer ?", "choices": ["Toujours", "Quand il se lit avec son parent et change peu", "Quand il est partagé par beaucoup de documents", "Quand il grossit sans limite"], "answer": "Quand il se lit avec son parent et change peu", "explanation": "On obtient tout en une lecture, sans risque de copies incohérentes."},
                {"type": "quiz", "id": "q2", "question": "À quoi sert le TTL d'une clé Redis ?", "choices": ["À la chiffrer", "À la faire expirer automatiquement", "À la répliquer", "À la trier"], "answer": "À la faire expirer automatiquement", "explanation": "Une valeur en cache ne doit pas vivre plus longtemps que sa fraîcheur acceptable."},
                {"type": "quiz", "id": "q3", "question": "La donnée d'origine change. Que faire de sa copie en cache ?", "choices": ["Rien", "L'invalider, c'est-à-dire supprimer la clé", "Redémarrer Redis", "Augmenter le TTL"], "answer": "L'invalider, c'est-à-dire supprimer la clé", "explanation": "Sinon l'application sert une valeur périmée jusqu'à l'expiration."},
                {"type": "quiz", "id": "q4", "question": "Peut-on faire de Redis la seule source de vérité des commandes d'un site marchand ?", "choices": ["Oui, c'est le plus rapide", "Non : on n'y range que ce qu'on sait reconstruire", "Oui, avec un TTL long", "Oui, si le serveur a beaucoup de mémoire"], "answer": "Non : on n'y range que ce qu'on sait reconstruire", "explanation": "La source de vérité reste une base durable ; Redis l'accélère."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-pipeline-agregation",
            "title": "Simuler un pipeline d'agrégation",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Écrivez `agreger(docs, pipeline)`, qui applique dans l'ordre une liste d'étapes à une liste de dictionnaires. Trois étapes sont à gérer :

- `{"$match": {cle: valeur, ...}}` garde les documents dont **tous** les champs correspondent ;
- `{"$group": {"_id": "$champ", "total": {"$sum": 1}}}` regroupe selon la valeur de `champ` et compte. Le résultat est une liste `[{"_id": valeur, "total": n}, ...]` ;
- `{"$sort": {cle: 1 ou -1}}` trie (1 : croissant, -1 : décroissant).

Pour `$group`, seul le compteur `{"$sum": 1}` est à gérer, sous le nom de clé fourni.''',
            "starter_code": '''def agreger(docs, pipeline):
    resultat = list(docs)
    for etape in pipeline:
        ...
    return resultat
''',
            "solution": '''def agreger(docs, pipeline):
    resultat = list(docs)
    for etape in pipeline:
        if "$match" in etape:
            criteres = etape["$match"]
            resultat = [
                d for d in resultat
                if all(d.get(k) == v for k, v in criteres.items())
            ]
        elif "$group" in etape:
            spec = etape["$group"]
            champ = spec["_id"].lstrip("$")
            nom = next(k for k in spec if k != "_id")
            compteurs = {}
            for doc in resultat:
                cle = doc.get(champ)
                compteurs[cle] = compteurs.get(cle, 0) + 1
            resultat = [{"_id": k, nom: v} for k, v in compteurs.items()]
        elif "$sort" in etape:
            for cle, sens in reversed(list(etape["$sort"].items())):
                resultat = sorted(resultat, key=lambda d: d.get(cle), reverse=(sens == -1))
    return resultat
''',
            "hints": [
                "`\"$exercise\".lstrip('$')` donne le nom du champ de regroupement.",
                "Le nom du compteur est la clé du `$group` qui n'est pas `_id`.",
                "Pour `$sort`, `sorted(..., reverse=(sens == -1))` suffit.",
            ],
            "spec": {"tests": [
                {"name": "match", "code": "docs = [{'u': 1, 'ok': True}, {'u': 2, 'ok': True}, {'u': 1, 'ok': False}]\nassert agreger(docs, [{'$match': {'u': 1}}]) == [{'u': 1, 'ok': True}, {'u': 1, 'ok': False}]"},
                {"name": "match_multiple", "code": "docs = [{'u': 1, 'ok': True}, {'u': 1, 'ok': False}]\nassert agreger(docs, [{'$match': {'u': 1, 'ok': True}}]) == [{'u': 1, 'ok': True}]"},
                {"name": "group", "code": "docs = [{'e': 'a'}, {'e': 'b'}, {'e': 'a'}]\nres = agreger(docs, [{'$group': {'_id': '$e', 'total': {'$sum': 1}}}])\nassert sorted(res, key=lambda d: d['_id']) == [{'_id': 'a', 'total': 2}, {'_id': 'b', 'total': 1}]"},
                {"name": "pipeline_complet", "code": "docs = [{'e': 'a', 'ok': True}, {'e': 'b', 'ok': True}, {'e': 'a', 'ok': True}, {'e': 'c', 'ok': False}]\nres = agreger(docs, [{'$match': {'ok': True}}, {'$group': {'_id': '$e', 'n': {'$sum': 1}}}, {'$sort': {'n': -1}}])\nassert res[0] == {'_id': 'a', 'n': 2}"},
                {"name": "tri_croissant", "code": "docs = [{'n': 3}, {'n': 1}, {'n': 2}]\nassert [d['n'] for d in agreger(docs, [{'$sort': {'n': 1}}])] == [1, 2, 3]"},
            ]},
        },
        {
            "slug": "quiz-nosql",
            "title": "SQL ou NoSQL ?",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "À chaque situation, son outil.",
            "spec": {"questions": [
                {"id": "1", "question": "Un catalogue de produits dont les caractéristiques varient beaucoup d'une catégorie à l'autre", "choices": ["Une base document", "Une base relationnelle normalisée", "Une base graphe", "Un fichier CSV"], "answer": "Une base document", "explanation": "Structure souple : chaque produit porte ses propres champs."},
                {"id": "2", "question": "Des virements bancaires entre comptes", "choices": ["Une base document", "Une base relationnelle avec transactions ACID", "Un cache Redis", "Une base en colonnes"], "answer": "Une base relationnelle avec transactions ACID", "explanation": "Débiter l'un sans créditer l'autre est inacceptable : il faut l'atomicité."},
                {"id": "3", "question": "Des suggestions d'amis dans un réseau social", "choices": ["Une base graphe", "Une base clé-valeur", "Une base en colonnes", "Du relationnel pur"], "answer": "Une base graphe", "explanation": "Parcourir des relations sur plusieurs niveaux, c'est le point fort du graphe."},
                {"id": "4", "question": "Que perd-on souvent en passant au NoSQL ?", "choices": ["La performance", "Les jointures et les contraintes d'intégrité", "Le typage", "La persistance"], "answer": "Les jointures et les contraintes d'intégrité", "explanation": "On duplique des données, et on valide dans l'application."},
                {"id": "5", "question": "Le résultat d'une requête lente, à garder cinq minutes", "choices": ["PostgreSQL", "Redis, avec un TTL", "Neo4j", "Un fichier CSV"], "answer": "Redis, avec un TTL", "explanation": "C'est le rôle d'un cache : rapide, temporaire, reconstructible."},
                {"id": "6", "question": "Des mesures de capteurs, écrites en masse et lues par plage de dates", "choices": ["Une base orientée colonnes ou séries temporelles", "Une base graphe", "Redis seul", "Un tableur"], "answer": "Une base orientée colonnes ou séries temporelles", "explanation": "Cassandra ou TimescaleDB sont conçues pour ces écritures massives."},
                {"id": "7", "question": "Quelle est la taille maximale d'un document MongoDB ?", "choices": ["1 Mo", "16 Mo", "1 Go", "Illimitée"], "answer": "16 Mo", "explanation": "D'où l'intérêt de sortir les tableaux qui grossissent sans fin."},
                {"id": "8", "question": "Sans index sur le champ filtré, que fait MongoDB ?", "choices": ["Il refuse la requête", "Il parcourt toute la collection", "Il crée l'index tout seul", "Il renvoie un résultat partiel"], "answer": "Il parcourt toute la collection", "explanation": "Comme en SQL : vérifiez avec `explain()`."},
            ]},
        },
    ],
}
