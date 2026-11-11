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
    (1, 'Alice', 'M1'), (2, 'Bob', 'M1'), (3, 'Chloe', 'M2'),
    (4, 'David', 'M2'), (5, 'Elena', 'M1'), (6, 'Farid', 'M2');

INSERT INTO cours (id, titre, credits) VALUES
    (1, 'Python', 6), (2, 'SQL', 4), (3, 'Machine Learning', 8), (4, 'Docker', 3);

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
    "summary": "SELECT, jointures, agregats, sous-requetes, index et transactions.",
    "category": "Donnees",
    "level": "debutant",
    "icon": "SQL",
    "lessons": [
        {
            "slug": "select-et-jointures",
            "title": "SELECT, filtres et jointures",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Ordre **logique** d'evaluation d'une requete (different de l'ordre d'ecriture) :\n\n`FROM` -> `JOIN` -> `WHERE` -> `GROUP BY` -> `HAVING` -> `SELECT` -> `ORDER BY` -> `LIMIT`\n\nC'est pour cela qu'on ne peut pas utiliser un alias du `SELECT` dans le `WHERE`, mais qu'on peut dans le `ORDER BY`."},
                {"type": "code", "lang": "sql", "code": "SELECT e.nom, c.titre, i.note\nFROM etudiants e\nJOIN inscriptions i ON i.etudiant_id = e.id\nJOIN cours c        ON c.id = i.cours_id\nWHERE i.note >= 12\nORDER BY i.note DESC;"},
                {"type": "text", "md": "Types de jointures :\n\n- `INNER JOIN` : seulement les lignes appariees des deux cotes.\n- `LEFT JOIN` : toutes les lignes de gauche, `NULL` a droite si rien ne correspond.\n- `CROSS JOIN` : produit cartesien (rarement voulu)."},
                {"type": "callout", "tone": "warn", "md": "`NULL` n'est egal a rien, pas meme a `NULL`. Utilisez `IS NULL` / `IS NOT NULL`. Et attention : `COUNT(colonne)` ignore les NULL, `COUNT(*)` les compte."},
                {"type": "quiz", "id": "q1", "question": "Je veux tous les etudiants, meme ceux sans inscription. Quelle jointure ?", "choices": ["INNER JOIN", "LEFT JOIN depuis etudiants", "RIGHT JOIN depuis inscriptions", "CROSS JOIN"], "answer": "LEFT JOIN depuis etudiants", "explanation": "La table de gauche est conservee entierement."},
                {"type": "quiz", "id": "q2", "question": "Difference entre WHERE et HAVING ?", "choices": ["Aucune", "WHERE filtre les lignes, HAVING filtre les groupes apres agregation", "HAVING est plus rapide", "WHERE ne marche pas avec les jointures"], "answer": "WHERE filtre les lignes, HAVING filtre les groupes apres agregation", "explanation": "HAVING intervient apres GROUP BY, donc peut porter sur AVG(), COUNT()..."},
            ],
        },
        {
            "slug": "agregats-index-transactions",
            "title": "Agregats, index et transactions",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "Un **agregat** resume un groupe de lignes : `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. Toute colonne du `SELECT` non agregee doit figurer dans le `GROUP BY`."},
                {"type": "code", "lang": "sql", "code": "SELECT c.titre,\n       COUNT(i.etudiant_id) AS inscrits,\n       ROUND(AVG(i.note), 2) AS moyenne\nFROM cours c\nLEFT JOIN inscriptions i ON i.cours_id = c.id\nGROUP BY c.id, c.titre\nHAVING COUNT(i.etudiant_id) >= 2\nORDER BY moyenne DESC;"},
                {"type": "text", "md": "Un **index** accelere la lecture (recherche en O(log n) au lieu d'un parcours complet) mais ralentit l'ecriture et prend de la place. On indexe les colonnes de jointure et celles des `WHERE` frequents."},
                {"type": "code", "lang": "sql", "code": "CREATE INDEX idx_inscriptions_cours ON inscriptions(cours_id);\nEXPLAIN QUERY PLAN SELECT * FROM inscriptions WHERE cours_id = 1;"},
                {"type": "text", "md": "Une **transaction** garantit les proprietes ACID : soit tout passe, soit rien.\n\n```sql\nBEGIN;\nUPDATE comptes SET solde = solde - 100 WHERE id = 1;\nUPDATE comptes SET solde = solde + 100 WHERE id = 2;\nCOMMIT;  -- ou ROLLBACK en cas d'erreur\n```"},
                {"type": "quiz", "id": "q1", "question": "Que signifie le A de ACID ?", "choices": ["Asynchrone", "Atomicite", "Agregation", "Availability"], "answer": "Atomicite", "explanation": "Atomicite, Coherence, Isolation, Durabilite."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-jointure-notes",
            "title": "TP SQL - Moyenne par cours",
            "kind": "sql",
            "difficulty": "facile",
            "statement": "La base contient `etudiants(id, nom, promo)`, `cours(id, titre, credits)` et `inscriptions(etudiant_id, cours_id, note)`.\n\nEcrivez une requete renvoyant **deux colonnes** : le titre du cours et la moyenne de ses notes, uniquement pour les cours ayant **au moins 2 notes non nulles**.\n\nL'ordre des lignes n'est pas verifie.",
            "starter_code": "SELECT ...\nFROM cours c\nJOIN inscriptions i ON ...\n",
            "solution": "SELECT c.titre, AVG(i.note) AS moyenne\nFROM cours c\nJOIN inscriptions i ON i.cours_id = c.id\nWHERE i.note IS NOT NULL\nGROUP BY c.id, c.titre\nHAVING COUNT(i.note) >= 2;",
            "hints": [
                "Jointure sur `i.cours_id = c.id`.",
                "Excluez les notes NULL avec `WHERE i.note IS NOT NULL`.",
                "Le filtre sur le nombre de notes se fait en HAVING, pas en WHERE.",
            ],
            "spec": {
                "schema": SCHEMA,
                "question": "titre du cours + moyenne, cours ayant >= 2 notes",
                "expected_query": "SELECT c.titre, AVG(i.note) FROM cours c JOIN inscriptions i ON i.cours_id = c.id WHERE i.note IS NOT NULL GROUP BY c.id, c.titre HAVING COUNT(i.note) >= 2",
                "ordered": False,
            },
        },
        {
            "slug": "tp-left-join",
            "title": "TP SQL - Etudiants sans bonne note",
            "kind": "sql",
            "difficulty": "moyen",
            "statement": "Renvoyez le **nom** des etudiants qui n'ont **aucune note >= 12** (y compris ceux qui n'ont aucune note du tout).\n\nUne seule colonne, ordre non verifie. Un `LEFT JOIN` ou une sous-requete `NOT EXISTS` fonctionnent tous les deux.",
            "starter_code": "SELECT e.nom\nFROM etudiants e\n",
            "solution": "SELECT e.nom\nFROM etudiants e\nWHERE NOT EXISTS (\n    SELECT 1 FROM inscriptions i\n    WHERE i.etudiant_id = e.id AND i.note >= 12\n);",
            "hints": [
                "`NOT EXISTS (SELECT 1 FROM inscriptions WHERE ... AND note >= 12)`.",
                "Variante : LEFT JOIN sur les inscriptions filtrees puis `GROUP BY` + `HAVING MAX(note) IS NULL`.",
                "Attention a ne pas exclure l'etudiant qui n'a aucune inscription.",
            ],
            "spec": {
                "schema": SCHEMA,
                "question": "noms des etudiants sans aucune note >= 12",
                "expected_query": "SELECT e.nom FROM etudiants e WHERE NOT EXISTS (SELECT 1 FROM inscriptions i WHERE i.etudiant_id = e.id AND i.note >= 12)",
                "ordered": False,
            },
        },
    ],
}
