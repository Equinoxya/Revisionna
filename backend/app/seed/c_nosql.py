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
            ]},
        },
    ],
}
