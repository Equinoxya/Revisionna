SCHEMA = """
CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    promo TEXT NOT NULL
);
CREATE TABLE cours (
    id INTEGER PRIMARY KEY,
    titre TEXT NOT NULL,
    credits INTEGER NOT NULL
);
CREATE TABLE inscriptions (
    etudiant_id INTEGER REFERENCES etudiants(id),
    cours_id INTEGER REFERENCES cours(id),
    note REAL
);

INSERT INTO etudiants (id, nom, promo) VALUES
    (1, 'Alice', 'M1'), (2, 'Bob', 'M1'), (3, 'Chloé', 'M2'),
    (4, 'David', 'M2'), (5, 'Elena', 'M1'), (6, 'Farid', 'M2');

INSERT INTO cours (id, titre, credits) VALUES
    (1, 'Python', 6), (2, 'SQL', 4), (3, 'Machine learning', 8), (4, 'Docker', 3);

INSERT INTO inscriptions (etudiant_id, cours_id, note) VALUES
    (1, 1, 16.0), (1, 2, 14.0), (1, 3, 11.5),
    (2, 1, 9.0),  (2, 2, 12.0),
    (3, 1, 18.0), (3, 3, 15.5), (3, 4, 13.0),
    (4, 2, 7.5),
    (5, 1, 12.0), (5, 4, NULL);
"""

COURSE = {
    "slug": "sql",
    "title": "SQL : bases relationnelles",
    "summary": "SELECT, jointures, agrégats, sous-requêtes, index et transactions.",
    "category": "Données",
    "level": "débutant",
    "icon": "SQL",
    "lessons": [
        {
            "slug": "select-et-jointures",
            "title": "SELECT, filtres et jointures",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''L'ordre dans lequel la base **évalue** une requête n'est pas celui dans lequel on l'écrit :

`FROM` → `JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`

C'est pour cela qu'un alias défini dans le `SELECT` est inutilisable dans le `WHERE`, mais utilisable dans le `ORDER BY`.'''},
                {"type": "code", "lang": "sql", "code": '''SELECT e.nom, c.titre, i.note
FROM etudiants e
JOIN inscriptions i ON i.etudiant_id = e.id
JOIN cours c        ON c.id = i.cours_id
WHERE i.note >= 12
ORDER BY i.note DESC;'''},
                {"type": "text", "md": '''Les jointures :

- `INNER JOIN` ne garde que les lignes qui ont une correspondance des deux côtés ;
- `LEFT JOIN` garde toutes les lignes de gauche, avec des `NULL` à droite quand rien ne correspond ;
- `CROSS JOIN` produit toutes les combinaisons possibles (rarement ce qu'on veut).'''},
                {"type": "callout", "tone": "warn", "md": "`NULL` n'est égal à rien, pas même à `NULL` : on teste avec `IS NULL` ou `IS NOT NULL`. Et attention, `COUNT(colonne)` ignore les `NULL`, alors que `COUNT(*)` les compte."},
                {"type": "quiz", "id": "q1", "question": "Je veux tous les étudiants, même ceux qui n'ont aucune inscription. Quelle jointure ?", "choices": ["INNER JOIN", "LEFT JOIN à partir de etudiants", "RIGHT JOIN à partir de etudiants", "CROSS JOIN"], "answer": "LEFT JOIN à partir de etudiants", "explanation": "La table de gauche est conservée en entier."},
                {"type": "quiz", "id": "q2", "question": "Quelle différence entre WHERE et HAVING ?", "choices": ["Aucune", "WHERE filtre les lignes, HAVING filtre les groupes après agrégation", "HAVING est plus rapide", "WHERE ne fonctionne pas avec les jointures"], "answer": "WHERE filtre les lignes, HAVING filtre les groupes après agrégation", "explanation": "`HAVING` intervient après le `GROUP BY` : il peut donc porter sur `AVG()`, `COUNT()`…"},
            ],
        },
        {
            "slug": "agregats-index-transactions",
            "title": "Agrégats, index et transactions",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Un **agrégat** résume un groupe de lignes : `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. Toute colonne du `SELECT` qui n'est pas agrégée doit figurer dans le `GROUP BY`."},
                {"type": "code", "lang": "sql", "code": '''SELECT c.titre,
       COUNT(i.etudiant_id) AS inscrits,
       ROUND(AVG(i.note), 2) AS moyenne
FROM cours c
LEFT JOIN inscriptions i ON i.cours_id = c.id
GROUP BY c.id, c.titre
HAVING COUNT(i.etudiant_id) >= 2
ORDER BY moyenne DESC;'''},
                {"type": "text", "md": "Un **index** accélère la lecture (une recherche en O(log n) au lieu d'un parcours complet), mais ralentit l'écriture et occupe de la place. On indexe les colonnes de jointure et celles des `WHERE` fréquents."},
                {"type": "code", "lang": "sql", "code": '''CREATE INDEX idx_inscriptions_cours ON inscriptions(cours_id);
EXPLAIN QUERY PLAN SELECT * FROM inscriptions WHERE cours_id = 1;'''},
                {"type": "text", "md": '''Une **transaction** garantit les propriétés ACID : soit tout passe, soit rien.

```sql
BEGIN;
UPDATE comptes SET solde = solde - 100 WHERE id = 1;
UPDATE comptes SET solde = solde + 100 WHERE id = 2;
COMMIT;  -- ou ROLLBACK en cas d'erreur
```'''},
                {"type": "quiz", "id": "q1", "question": "Que désigne le A de ACID ?", "choices": ["Asynchrone", "Atomicité", "Agrégation", "Accessibilité"], "answer": "Atomicité", "explanation": "Atomicité, Cohérence, Isolation, Durabilité."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-jointure-notes",
            "title": "Moyenne par cours",
            "kind": "sql",
            "difficulty": "facile",
            "statement": '''La base contient `etudiants(id, nom, promo)`, `cours(id, titre, credits)` et `inscriptions(etudiant_id, cours_id, note)`.

Écrivez une requête qui renvoie **deux colonnes**, le titre du cours et la moyenne de ses notes, uniquement pour les cours ayant **au moins 2 notes renseignées**.

L'ordre des lignes n'est pas vérifié.''',
            "starter_code": '''SELECT ...
FROM cours c
JOIN inscriptions i ON ...
''',
            "solution": '''SELECT c.titre, AVG(i.note) AS moyenne
FROM cours c
JOIN inscriptions i ON i.cours_id = c.id
WHERE i.note IS NOT NULL
GROUP BY c.id, c.titre
HAVING COUNT(i.note) >= 2;''',
            "hints": [
                "La jointure se fait sur `i.cours_id = c.id`.",
                "Écartez les notes vides avec `WHERE i.note IS NOT NULL`.",
                "Le filtre sur le nombre de notes se place dans `HAVING`, pas dans `WHERE`.",
            ],
            "spec": {
                "schema": SCHEMA,
                "expected_query": "SELECT c.titre, AVG(i.note) FROM cours c JOIN inscriptions i ON i.cours_id = c.id WHERE i.note IS NOT NULL GROUP BY c.id, c.titre HAVING COUNT(i.note) >= 2",
                "ordered": False,
            },
        },
        {
            "slug": "tp-left-join",
            "title": "Les étudiants sans bonne note",
            "kind": "sql",
            "difficulty": "moyen",
            "statement": '''Renvoyez le **nom** des étudiants qui n'ont **aucune note supérieure ou égale à 12**, y compris ceux qui n'ont aucune note du tout.

Une seule colonne ; l'ordre n'est pas vérifié. Un `LEFT JOIN` comme une sous-requête `NOT EXISTS` font l'affaire.''',
            "starter_code": '''SELECT e.nom
FROM etudiants e
''',
            "solution": '''SELECT e.nom
FROM etudiants e
WHERE NOT EXISTS (
    SELECT 1 FROM inscriptions i
    WHERE i.etudiant_id = e.id AND i.note >= 12
);''',
            "hints": [
                "`NOT EXISTS (SELECT 1 FROM inscriptions WHERE ... AND note >= 12)`.",
                "Variante : un `LEFT JOIN` sur les inscriptions filtrées, puis `GROUP BY` et `HAVING MAX(note) IS NULL`.",
                "Veillez à ne pas écarter l'étudiant qui n'a aucune inscription.",
            ],
            "spec": {
                "schema": SCHEMA,
                "expected_query": "SELECT e.nom FROM etudiants e WHERE NOT EXISTS (SELECT 1 FROM inscriptions i WHERE i.etudiant_id = e.id AND i.note >= 12)",
                "ordered": False,
            },
        },
    ],
}
