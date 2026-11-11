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
    ],
}
