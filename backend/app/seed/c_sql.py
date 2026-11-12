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
                {"type": "quiz", "id": "q2", "question": "Quel est le prix d'un index ?", "choices": ["Aucun", "Des écritures plus lentes et de l'espace disque", "Des lectures plus lentes", "La perte des transactions"], "answer": "Des écritures plus lentes et de l'espace disque", "explanation": "Chaque INSERT ou UPDATE doit aussi mettre l'index à jour."},
                {"type": "quiz", "id": "q3", "question": "Dans une transaction, que fait ROLLBACK ?", "choices": ["Il valide les changements", "Il annule tout ce qui a été fait depuis BEGIN", "Il supprime la table", "Il crée une sauvegarde"], "answer": "Il annule tout ce qui a été fait depuis BEGIN", "explanation": "Soit tout passe (COMMIT), soit rien (ROLLBACK)."},
            ],
        },
        {
            "slug": "modelisation-et-contraintes",
            "title": "Modéliser : clés, contraintes et normalisation",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Avant d'écrire des requêtes, il faut des tables bien conçues. Deux notions fondent le modèle relationnel :

- la **clé primaire** identifie chaque ligne de manière unique : jamais vide, jamais en double ;
- la **clé étrangère** désigne une ligne d'une autre table, et la base **refuse** toute valeur qui ne correspond à rien.

Les **contraintes** confient à la base le soin de garder les données cohérentes, quel que soit le programme qui écrit dedans.'''},
                {"type": "code", "lang": "sql", "code": '''CREATE TABLE etudiants (
    id     INTEGER PRIMARY KEY,
    nom    TEXT NOT NULL,
    email  TEXT NOT NULL UNIQUE
);

CREATE TABLE inscriptions (
    etudiant_id INTEGER NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    cours_id    INTEGER NOT NULL REFERENCES cours(id),
    note        REAL CHECK (note BETWEEN 0 AND 20),
    PRIMARY KEY (etudiant_id, cours_id)      -- une seule inscription par cours
);'''},
                {"type": "text", "md": '''| Contrainte | Garantie |
|---|---|
| `PRIMARY KEY` | identifiant unique et non nul |
| `FOREIGN KEY` / `REFERENCES` | la ligne désignée existe |
| `NOT NULL` | la valeur est obligatoire |
| `UNIQUE` | pas de doublon |
| `CHECK` | une condition toujours vraie |
| `DEFAULT` | une valeur quand on n'en fournit pas |

Les relations entre tables sont de trois sortes :

- **un à plusieurs** : un cours a plusieurs leçons. La clé étrangère va du côté « plusieurs » (`lecons.cours_id`) ;
- **plusieurs à plusieurs** : un étudiant suit plusieurs cours, un cours a plusieurs étudiants. Il faut une **table de liaison** (`inscriptions`) ;
- **un à un** : plus rare, par exemple un compte et son profil.'''},
                {"type": "text", "md": '''**Normaliser**, c'est ranger chaque information à **un seul endroit**. Si le nom d'un cours est recopié dans chaque inscription, le jour où il change, il faut le corriger partout — et on en oubliera.

- **1re forme normale** : une seule valeur par case (pas de liste `"python, sql"` dans une colonne) ;
- **2e forme normale** : chaque colonne dépend de toute la clé, pas d'une partie seulement ;
- **3e forme normale** : chaque colonne dépend de la clé, et de rien d'autre.

En pratique : une table par « chose », et des clés étrangères pour les relier.'''},
                {"type": "text", "md": '''Une requête peut en contenir une autre. La **sous-requête** se place dans un `WHERE` ou un `FROM` ; la **CTE** (`WITH`) lui donne un nom, ce qui rend les requêtes longues beaucoup plus lisibles.'''},
                {"type": "code", "lang": "sql", "code": '''-- les étudiants dont la moyenne dépasse la moyenne générale
WITH moyennes AS (
    SELECT etudiant_id, AVG(note) AS moyenne
    FROM inscriptions
    GROUP BY etudiant_id
)
SELECT e.nom, m.moyenne
FROM moyennes m
JOIN etudiants e ON e.id = m.etudiant_id
WHERE m.moyenne > (SELECT AVG(note) FROM inscriptions)
ORDER BY m.moyenne DESC;'''},
                {"type": "callout", "tone": "warn", "md": '''N'assemblez **jamais** une requête en collant du texte venu de l'utilisateur : c'est la porte ouverte à l'**injection SQL**. Passez les valeurs en **paramètres**, la base les traite alors comme des données, jamais comme du code.

```python
# dangereux
cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
# correct
cur.execute("SELECT * FROM users WHERE email = %s", (email,))
```'''},
                {"type": "quiz", "id": "q1", "question": "Que garantit une clé étrangère ?", "choices": ["L'unicité de la ligne", "Que la ligne désignée existe dans l'autre table", "Que la colonne n'est jamais vide", "Que la requête est rapide"], "answer": "Que la ligne désignée existe dans l'autre table", "explanation": "C'est l'intégrité référentielle : pas d'inscription à un cours inexistant."},
                {"type": "quiz", "id": "q2", "question": "Comment modéliser une relation plusieurs à plusieurs ?", "choices": ["Avec une colonne contenant une liste", "Avec une table de liaison", "Avec deux clés primaires dans la même table", "C'est impossible en SQL"], "answer": "Avec une table de liaison", "explanation": "Elle contient une clé étrangère vers chacune des deux tables."},
                {"type": "quiz", "id": "q3", "question": "Comment se protéger d'une injection SQL ?", "choices": ["En masquant les messages d'erreur", "Avec des requêtes paramétrées", "En utilisant POST plutôt que GET", "En chiffrant la base"], "answer": "Avec des requêtes paramétrées", "explanation": "Les valeurs ne sont jamais interprétées comme du SQL."},
                {"type": "quiz", "id": "q4", "question": "Le titre du cours est recopié dans chaque ligne d'inscription. Quel est le risque ?", "choices": ["Aucun", "Des incohérences dès que le titre change", "Des requêtes plus rapides", "Une erreur de syntaxe"], "answer": "Des incohérences dès que le titre change", "explanation": "Normaliser, c'est ne ranger chaque information qu'à un seul endroit."},
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
        {
            "slug": "quiz-sql",
            "title": "SQL, l'essentiel",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Les mots-clés et les pièges les plus fréquents.",
            "spec": {"questions": [
                {"id": "1", "question": "Quelle clause trie le résultat ?", "choices": ["GROUP BY", "ORDER BY", "HAVING", "LIMIT"], "answer": "ORDER BY", "explanation": "`ORDER BY colonne DESC` pour un tri décroissant."},
                {"id": "2", "question": "Comment tester qu'une note est absente ?", "choices": ["note = NULL", "note IS NULL", "note == NULL", "note = ''"], "answer": "note IS NULL", "explanation": "`NULL` n'est égal à rien : `= NULL` ne renvoie jamais vrai."},
                {"id": "3", "question": "Que compte `COUNT(note)` ?", "choices": ["Toutes les lignes", "Les lignes où note n'est pas NULL", "La somme des notes", "Les notes distinctes"], "answer": "Les lignes où note n'est pas NULL", "explanation": "`COUNT(*)` compte toutes les lignes, `COUNT(colonne)` ignore les `NULL`."},
                {"id": "4", "question": "Quelle commande supprime des lignes ?", "choices": ["DROP", "DELETE", "REMOVE", "TRUNCATE COLUMN"], "answer": "DELETE", "explanation": "`DELETE` supprime des lignes ; `DROP` supprime la table entière."},
                {"id": "5", "question": "Que se passe-t-il avec `UPDATE cours SET publie = 0;` sans WHERE ?", "choices": ["Rien", "Toutes les lignes sont modifiées", "Une erreur de syntaxe", "Seule la première ligne change"], "answer": "Toutes les lignes sont modifiées", "explanation": "Un `UPDATE` ou un `DELETE` sans `WHERE` s'applique à toute la table."},
                {"id": "6", "question": "Que renvoie un INNER JOIN pour un étudiant sans inscription ?", "choices": ["Une ligne avec des NULL", "Aucune ligne", "Une erreur", "Toutes les inscriptions"], "answer": "Aucune ligne", "explanation": "Pour le garder, il faut un `LEFT JOIN`."},
                {"id": "7", "question": "À quoi sert DISTINCT ?", "choices": ["À trier", "À éliminer les doublons du résultat", "À compter", "À joindre deux tables"], "answer": "À éliminer les doublons du résultat", "explanation": "`SELECT DISTINCT ville FROM etudiants`."},
                {"id": "8", "question": "Quelle contrainte interdit deux comptes avec le même e-mail ?", "choices": ["NOT NULL", "UNIQUE", "CHECK", "DEFAULT"], "answer": "UNIQUE", "explanation": "La base refuse le doublon, quel que soit le programme qui écrit."},
            ]},
        },
    ],
}
