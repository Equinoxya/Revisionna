COURSE = {
    "slug": "machine-learning",
    "title": "Machine learning : les bases",
    "summary": "Apprentissage supervisé ou non, jeux d'entraînement et de test, métriques, surapprentissage, pipeline scikit-learn.",
    "category": "Données",
    "level": "intermédiaire",
    "icon": "ML",
    "lessons": [
        {
            "slug": "vocabulaire-et-protocole",
            "title": "Vocabulaire et protocole expérimental",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Trois familles d'apprentissage :

- **supervisé** : on dispose d'étiquettes. Régression (prédire une valeur) ou classification (prédire une classe) ;
- **non supervisé** : pas d'étiquettes. Regroupement, réduction de dimension ;
- **par renforcement** : un agent apprend à force de récompenses.

Le protocole minimal : séparer les données en un jeu d'**entraînement** et un jeu de **test**, apprendre sur le premier, mesurer sur le second.'''},
                {"type": "code", "lang": "python", "code": '''from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

modele = make_pipeline(StandardScaler(), LogisticRegression())
modele.fit(X_train, y_train)
print(modele.score(X_test, y_test))'''},
                {"type": "callout", "tone": "warn", "md": "**Fuite de données** : si vous normalisez avant de séparer, la moyenne du jeu de test se retrouve dans l'entraînement. Placez toujours le prétraitement **dans** le pipeline."},
                {"type": "text", "md": "**Surapprentissage** : un score élevé à l'entraînement et médiocre au test signale que le modèle a mémorisé au lieu d'apprendre. Les remèdes : davantage de données, un modèle plus simple, de la régularisation, une validation croisée."},
                {"type": "quiz", "id": "q1", "question": "Entraînement 0,99 et test 0,62 : quel diagnostic ?", "choices": ["Sous-apprentissage", "Surapprentissage", "Fuite de données", "Le modèle est parfait"], "answer": "Surapprentissage", "explanation": "Un grand écart entre entraînement et test, c'est la signature du surapprentissage."},
                {"type": "quiz", "id": "q2", "question": "À quoi sert `stratify=y` ?", "choices": ["À mélanger les données", "À conserver les proportions de chaque classe dans les deux jeux", "À normaliser", "À accélérer le calcul"], "answer": "À conserver les proportions de chaque classe dans les deux jeux", "explanation": "Indispensable quand les classes sont déséquilibrées."},
            ],
        },
        {
            "slug": "metriques",
            "title": "Choisir la bonne métrique",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": '''Sur un jeu déséquilibré, l'exactitude (*accuracy*) ment : avec 99 % de négatifs, un modèle qui répond toujours « négatif » obtient 99 %.

On part donc de la matrice de confusion (vrais et faux positifs, vrais et faux négatifs) :

- **précision** = VP / (VP + FP) : parmi mes alertes, combien sont justifiées ?
- **rappel** = VP / (VP + FN) : parmi les cas réels, combien ai-je détectés ?
- **F1** = moyenne harmonique des deux.'''},
                {"type": "code", "lang": "python", "code": '''from sklearn.metrics import classification_report, confusion_matrix

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, digits=3))'''},
                {"type": "text", "md": "Le bon choix dépend du coût de l'erreur. Pour un dépistage médical, on privilégie le **rappel** (ne laisser passer aucun cas) ; pour un filtre antispam, la **précision** (ne pas jeter un vrai message)."},
                {"type": "quiz", "id": "q1", "question": "Détection de fraude, 0,1 % de cas positifs. Quelle métrique regarder ?", "choices": ["L'exactitude", "Le rappel et la précision (ou le F1)", "Le R²", "L'erreur quadratique moyenne"], "answer": "Le rappel et la précision (ou le F1)", "explanation": "Sur un déséquilibre aussi fort, l'exactitude ne dit rien."},
                {"type": "quiz", "id": "q2", "question": "Que mesure la précision ?", "choices": ["La part des vrais positifs retrouvés", "Parmi les prédictions positives, la part qui l'est vraiment", "La part de bonnes réponses, toutes classes confondues", "La vitesse du modèle"], "answer": "Parmi les prédictions positives, la part qui l'est vraiment", "explanation": "Précision = VP / (VP + FP). Le rappel, lui, vaut VP / (VP + FN)."},
                {"type": "quiz", "id": "q3", "question": "Un filtre anti-spam ne doit surtout pas classer un vrai message en spam. Que privilégier ?", "choices": ["Le rappel", "La précision", "L'exactitude", "La vitesse"], "answer": "La précision", "explanation": "On veut peu de faux positifs, quitte à laisser passer quelques spams."},
            ],
        },
        {
            "slug": "preparation-pipeline-et-validation",
            "title": "Préparer les données, pipeline et validation croisée",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Un modèle n'apprend que des **nombres**, et de préférence des nombres propres. La préparation occupe l'essentiel du temps d'un projet :

| Problème | Réponse courante |
|---|---|
| valeurs manquantes | les remplacer par la médiane ou la valeur la plus fréquente (`SimpleImputer`) |
| variable catégorielle (`"Paris"`, `"Lyon"`) | une colonne par catégorie (`OneHotEncoder`) |
| échelles très différentes (âge, salaire) | centrer et réduire (`StandardScaler`) |
| valeurs aberrantes | les comprendre avant de les supprimer |

Toutes ces transformations s'**apprennent** sur les données : la médiane, la moyenne, la liste des catégories. Elles doivent donc s'apprendre sur le jeu d'**entraînement seulement**.'''},
                {"type": "text", "md": '''Le **Pipeline** enchaîne les étapes de préparation et le modèle dans un seul objet. `fit` apprend tout sur l'entraînement ; `predict` réapplique exactement les mêmes transformations. La fuite de données devient impossible par construction.'''},
                {"type": "code", "lang": "python", "code": '''from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeriques = ["age", "revenu"]
categorielles = ["ville"]

preparation = ColumnTransformer([
    ("num", Pipeline([
        ("manquants", SimpleImputer(strategy="median")),
        ("echelle", StandardScaler()),
    ]), numeriques),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorielles),
])

modele = Pipeline([
    ("preparation", preparation),
    ("classifieur", LogisticRegression(max_iter=1000)),
])

modele.fit(X_train, y_train)
print(modele.score(X_test, y_test))'''},
                {"type": "text", "md": '''Un seul découpage entraînement / test peut tomber sur un cas favorable. La **validation croisée** découpe l'entraînement en `k` parts : le modèle s'entraîne sur `k - 1` parts, s'évalue sur la dernière, et on recommence `k` fois. On obtient une moyenne **et** un écart-type, donc une idée de la stabilité du résultat.'''},
                {"type": "code", "lang": "python", "code": '''from sklearn.model_selection import GridSearchCV, cross_val_score

scores = cross_val_score(modele, X_train, y_train, cv=5, scoring="f1")
print(f"F1 : {scores.mean():.3f} ± {scores.std():.3f}")

# chercher les meilleurs hyperparamètres, toujours par validation croisée
recherche = GridSearchCV(
    modele,
    param_grid={"classifieur__C": [0.01, 0.1, 1, 10]},
    cv=5,
    scoring="f1",
)
recherche.fit(X_train, y_train)
print(recherche.best_params_, recherche.best_score_)'''},
                {"type": "text", "md": '''Un **paramètre** est appris par le modèle (les coefficients d'une régression). Un **hyperparamètre** est choisi par vous avant l'entraînement (le `k` des plus proches voisins, la profondeur d'un arbre).

Le compromis à garder en tête :

- modèle **trop simple** : il se trompe partout, à l'entraînement comme au test. C'est le **sous-apprentissage** (biais élevé) ;
- modèle **trop complexe** : parfait à l'entraînement, mauvais au test. C'est le **surapprentissage** (variance élevée).'''},
                {"type": "callout", "tone": "warn", "md": "Le jeu de **test** ne sert qu'**une fois**, à la toute fin. Si vous l'utilisez pour choisir vos hyperparamètres, vous l'avez appris sans le dire : votre score final sera trop optimiste. Les réglages se font par validation croisée sur l'entraînement."},
                {"type": "callout", "tone": "info", "md": "Commencez toujours par un **modèle de référence** très simple (prédire la classe majoritaire, ou la moyenne). Un modèle sophistiqué qui ne le bat pas nettement ne vaut pas sa complexité."},
                {"type": "quiz", "id": "q1", "question": "Quel est l'intérêt principal d'un Pipeline ?", "choices": ["Aller plus vite", "Appliquer les mêmes transformations à l'entraînement et à la prédiction, sans fuite", "Se passer de jeu de test", "Augmenter l'exactitude"], "answer": "Appliquer les mêmes transformations à l'entraînement et à la prédiction, sans fuite", "explanation": "Les transformations ne sont apprises que sur les données d'entraînement."},
                {"type": "quiz", "id": "q2", "question": "Que fournit une validation croisée à 5 plis ?", "choices": ["Un seul score", "Cinq scores, donc une moyenne et une dispersion", "Cinq modèles à déployer", "Un jeu de test plus grand"], "answer": "Cinq scores, donc une moyenne et une dispersion", "explanation": "L'écart-type indique si le résultat est stable."},
                {"type": "quiz", "id": "q3", "question": "Le k des plus proches voisins est...", "choices": ["Un paramètre appris", "Un hyperparamètre choisi avant l'entraînement", "Une métrique", "Une étiquette"], "answer": "Un hyperparamètre choisi avant l'entraînement", "explanation": "On le règle par validation croisée."},
                {"type": "quiz", "id": "q4", "question": "Mauvais score à l'entraînement ET au test : quel diagnostic ?", "choices": ["Surapprentissage", "Sous-apprentissage", "Fuite de données", "Jeu de test trop grand"], "answer": "Sous-apprentissage", "explanation": "Le modèle est trop simple, ou les variables n'expliquent pas la cible."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-metriques",
            "title": "Calculer précision, rappel et F1",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Sans scikit-learn, écrivez les métriques d'une classification binaire. `y_vrai` et `y_pred` sont deux listes de 0 et de 1, de même longueur.

- `matrice_confusion(y_vrai, y_pred)` renvoie `{"vp": ..., "fp": ..., "vn": ..., "fn": ...}` ;
- `precision(y_vrai, y_pred)` renvoie `vp / (vp + fp)`, et `0.0` si le dénominateur est nul ;
- `rappel(y_vrai, y_pred)` renvoie `vp / (vp + fn)`, et `0.0` si le dénominateur est nul ;
- `f1(y_vrai, y_pred)` renvoie la moyenne harmonique des deux, et `0.0` si elles sont nulles toutes les deux.''',
            "starter_code": '''def matrice_confusion(y_vrai, y_pred):
    ...


def precision(y_vrai, y_pred):
    ...


def rappel(y_vrai, y_pred):
    ...


def f1(y_vrai, y_pred):
    ...
''',
            "solution": '''def matrice_confusion(y_vrai, y_pred):
    m = {"vp": 0, "fp": 0, "vn": 0, "fn": 0}
    for vrai, pred in zip(y_vrai, y_pred):
        if vrai == 1 and pred == 1:
            m["vp"] += 1
        elif vrai == 0 and pred == 1:
            m["fp"] += 1
        elif vrai == 0 and pred == 0:
            m["vn"] += 1
        else:
            m["fn"] += 1
    return m


def precision(y_vrai, y_pred):
    m = matrice_confusion(y_vrai, y_pred)
    denominateur = m["vp"] + m["fp"]
    return m["vp"] / denominateur if denominateur else 0.0


def rappel(y_vrai, y_pred):
    m = matrice_confusion(y_vrai, y_pred)
    denominateur = m["vp"] + m["fn"]
    return m["vp"] / denominateur if denominateur else 0.0


def f1(y_vrai, y_pred):
    p, r = precision(y_vrai, y_pred), rappel(y_vrai, y_pred)
    return 2 * p * r / (p + r) if (p + r) else 0.0
''',
            "hints": [
                "Parcourez les deux listes ensemble avec `zip`.",
                "Réutilisez `matrice_confusion` dans les trois autres fonctions.",
                "Vérifiez toujours le dénominateur avant de diviser.",
            ],
            "spec": {"tests": [
                {"name": "confusion", "code": "assert matrice_confusion([1,0,1,0], [1,1,0,0]) == {'vp': 1, 'fp': 1, 'vn': 1, 'fn': 1}"},
                {"name": "precision", "code": "assert abs(precision([1,0,1,0], [1,1,0,0]) - 0.5) < 1e-9"},
                {"name": "rappel", "code": "assert abs(rappel([1,0,1,0], [1,1,0,0]) - 0.5) < 1e-9"},
                {"name": "f1", "code": "assert abs(f1([1,0,1,0], [1,1,0,0]) - 0.5) < 1e-9"},
                {"name": "aucune_prediction_positive", "code": "assert precision([1,1], [0,0]) == 0.0 and f1([1,1], [0,0]) == 0.0"},
                {"name": "parfait", "code": "assert f1([1,0,1], [1,0,1]) == 1.0"},
            ]},
        },
        {
            "slug": "tp-knn",
            "title": "Les k plus proches voisins, à la main",
            "kind": "python",
            "difficulty": "difficile",
            "statement": '''Les k plus proches voisins sont l'algorithme supervisé le plus simple : pas de phase d'apprentissage, on compare aux exemples connus.

Écrivez :

- `distance(a, b)` : la distance euclidienne entre deux points (des tuples de même dimension) ;
- `predire(entrainement, point, k=3)` : `entrainement` est une liste de couples `(point, etiquette)`. Renvoyez l'étiquette majoritaire parmi les `k` plus proches voisins. En cas d'égalité, renvoyez celle du voisin le plus proche.

Aucun import n'est autorisé, pas même `math` : utilisez `** 0.5`.''',
            "starter_code": '''def distance(a, b):
    ...


def predire(entrainement, point, k=3):
    ...
''',
            "solution": '''def distance(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def predire(entrainement, point, k=3):
    voisins = sorted(entrainement, key=lambda item: distance(item[0], point))[:k]
    compte = {}
    for _, etiquette in voisins:
        compte[etiquette] = compte.get(etiquette, 0) + 1
    maximum = max(compte.values())
    gagnantes = [e for e, n in compte.items() if n == maximum]
    if len(gagnantes) == 1:
        return gagnantes[0]
    return voisins[0][1]
''',
            "hints": [
                "Pour la distance : `sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5`.",
                "Triez les exemples par distance au point, puis gardez les `k` premiers.",
                "Comptez les étiquettes dans un dictionnaire ; en cas d'égalité, le premier voisin décide.",
            ],
            "spec": {"tests": [
                {"name": "distance", "code": "assert abs(distance((0, 0), (3, 4)) - 5.0) < 1e-9"},
                {"name": "distance_nulle", "code": "assert abs(distance((1, 1, 1), (1, 1, 1))) < 1e-9"},
                {"name": "predire_simple", "code": "train = [((0, 0), 'a'), ((0, 1), 'a'), ((10, 10), 'b')]\nassert predire(train, (0, 0.5), k=3) == 'a'"},
                {"name": "predire_k1", "code": "train = [((0, 0), 'a'), ((10, 10), 'b')]\nassert predire(train, (9, 9), k=1) == 'b'"},
                {"name": "egalite", "code": "train = [((0, 0), 'a'), ((5, 0), 'b')]\nassert predire(train, (1, 0), k=2) == 'a'"},
            ]},
        },
        {
            "slug": "quiz-ml",
            "title": "Le vocabulaire du machine learning",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Les notions à ne pas confondre.",
            "spec": {"questions": [
                {"id": "1", "question": "Prédire le prix d'un appartement, c'est...", "choices": ["Une classification", "Une régression", "Un regroupement", "Une réduction de dimension"], "answer": "Une régression", "explanation": "On prédit une valeur continue, pas une catégorie."},
                {"id": "2", "question": "Regrouper des clients sans étiquette connue, c'est...", "choices": ["De l'apprentissage supervisé", "De l'apprentissage non supervisé", "De la régression", "De la validation croisée"], "answer": "De l'apprentissage non supervisé", "explanation": "Sans étiquettes, l'algorithme cherche lui-même une structure (*clustering*)."},
                {"id": "3", "question": "À quoi sert le jeu de test ?", "choices": ["À entraîner le modèle", "À estimer la performance sur des données jamais vues", "À choisir les hyperparamètres", "À nettoyer les données"], "answer": "À estimer la performance sur des données jamais vues", "explanation": "Il ne sert qu'une fois, à la fin."},
                {"id": "4", "question": "Qu'est-ce qu'un faux négatif ?", "choices": ["Un positif prédit négatif", "Un négatif prédit positif", "Une bonne prédiction", "Une donnée manquante"], "answer": "Un positif prédit négatif", "explanation": "Le malade que le dépistage n'a pas vu."},
                {"id": "5", "question": "Comment encoder une colonne « ville » ?", "choices": ["En numérotant les villes de 1 à n", "Avec une colonne par ville (one-hot)", "En la supprimant toujours", "En prenant la longueur du nom"], "answer": "Avec une colonne par ville (one-hot)", "explanation": "Numéroter créerait un ordre et des distances qui n'existent pas."},
                {"id": "6", "question": "Pourquoi normaliser avant un k plus proches voisins ?", "choices": ["Pour aller plus vite", "Pour qu'une variable à grande échelle n'écrase pas les autres dans la distance", "C'est inutile", "Pour supprimer les valeurs manquantes"], "answer": "Pour qu'une variable à grande échelle n'écrase pas les autres dans la distance", "explanation": "Un salaire en euros pèserait mille fois plus qu'un âge en années."},
                {"id": "7", "question": "Que combine le score F1 ?", "choices": ["Exactitude et vitesse", "Précision et rappel", "Biais et variance", "Entraînement et test"], "answer": "Précision et rappel", "explanation": "C'est leur moyenne harmonique : il est faible dès que l'un des deux l'est."},
                {"id": "8", "question": "Votre modèle atteint 95 % d'exactitude ; la classe majoritaire représente 95 % des données. Qu'en conclure ?", "choices": ["Le modèle est excellent", "Il ne fait pas mieux que répondre toujours la classe majoritaire", "Il surapprend", "Il faut plus de données de test"], "answer": "Il ne fait pas mieux que répondre toujours la classe majoritaire", "explanation": "D'où l'importance d'un modèle de référence."},
            ]},
        },
    ],
}
