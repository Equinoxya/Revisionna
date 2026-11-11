COURSE = {
    "slug": "react",
    "title": "React : interfaces à composants",
    "summary": "JSX, état, effets, hooks personnalisés, listes et formulaires contrôlés.",
    "category": "Frontend",
    "level": "intermédiaire",
    "icon": "Re",
    "lessons": [
        {
            "slug": "composants-et-etat",
            "title": "Composants, props et état",
            "duration_min": 15,
            "blocks": [
                {"type": "text", "md": "Un composant React est une fonction qui reçoit des **props** et renvoie du JSX. L'affichage est une fonction de l'état : on ne touche pas au DOM à la main, on modifie l'état et React recalcule."},
                {"type": "code", "lang": "jsx", "code": '''function Compteur({ pas = 1 }) {
  const [valeur, setValeur] = useState(0);

  return (
    <button onClick={() => setValeur((v) => v + pas)}>
      Clics : {valeur}
    </button>
  );
}'''},
                {"type": "callout", "tone": "warn", "md": "Passez une **fonction** à `setValeur` quand la nouvelle valeur dépend de l'ancienne. Deux `setValeur(valeur + 1)` à la suite n'ajoutent qu'une unité."},
                {"type": "text", "md": "Règles des hooks : on les appelle au premier niveau du composant, jamais dans une condition ni dans une boucle. Leur ordre d'appel doit rester le même d'un rendu à l'autre."},
                {"type": "quiz", "id": "q1", "question": "Pourquoi donner une `key` aux éléments d'une liste ?", "choices": ["Pour le style", "Pour que React reconnaisse chaque élément d'un rendu à l'autre", "C'est facultatif et décoratif", "Pour trier la liste"], "answer": "Pour que React reconnaisse chaque élément d'un rendu à l'autre", "explanation": "Sans clé stable, React recrée les éléments et perd leur état. Évitez l'index comme clé si la liste peut être réordonnée."},
                {"type": "quiz", "id": "q2", "question": "Où peut-on appeler un hook ?", "choices": ["N'importe où", "Au premier niveau d'un composant ou d'un hook personnalisé", "Dans un if", "Dans une boucle"], "answer": "Au premier niveau d'un composant ou d'un hook personnalisé", "explanation": "React s'appuie sur l'ordre d'appel des hooks pour retrouver leur état."},
            ],
        },
        {
            "slug": "effets-et-hooks",
            "title": "Effets et hooks personnalisés",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": "`useEffect` synchronise le composant avec l'extérieur : appel réseau, abonnement, minuterie. Le tableau de dépendances indique **quand** rejouer l'effet."},
                {"type": "code", "lang": "jsx", "code": '''function useCours(slug) {
  const [cours, setCours] = useState(null);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    let annule = false;
    fetch(`/api/courses/${slug}`)
      .then((r) => r.json())
      .then((d) => { if (!annule) setCours(d.course); })
      .catch((e) => { if (!annule) setErreur(e.message); });
    return () => { annule = true; };   // nettoyage
  }, [slug]);

  return { cours, erreur };
}'''},
                {"type": "callout", "tone": "info", "md": "La fonction renvoyée par `useEffect` est le **nettoyage** : elle évite d'écrire dans un composant qui a déjà disparu de l'écran."},
                {"type": "text", "md": "Un **hook personnalisé** est une simple fonction dont le nom commence par `use` et qui appelle d'autres hooks. C'est le moyen de partager de la logique entre composants : voyez `frontend/src/lib/useApi.js` et `AuthContext.jsx` dans cette application."},
                {"type": "quiz", "id": "q1", "question": "Que fait un `useEffect` dont le tableau de dépendances est `[]` ?", "choices": ["Il ne s'exécute jamais", "Il s'exécute à chaque rendu", "Il s'exécute une fois, au montage", "Il boucle"], "answer": "Il s'exécute une fois, au montage", "explanation": "Aucune dépendance, donc aucun motif de le rejouer (deux passages en mode strict, pendant le développement)."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-reducer",
            "title": "La logique d'un reducer",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Un *reducer* est une fonction pure `(etat, action) → nouvel_etat`. C'est le cœur de `useReducer` et de Redux. On l'écrit ici en Python, pour en tester la logique.

`reducer(etat, action)` reçoit `etat = {"items": [...], "filtre": "tous"}` et `action = {"type": ..., ...}` :

- `ajouter` (clé `texte`) ajoute `{"texte": ..., "fait": False}` à la fin ;
- `basculer` (clé `index`) inverse le champ `fait` de l'élément ;
- `filtrer` (clé `valeur`) remplace `filtre` ;
- un type inconnu renvoie l'état **inchangé**.

Contrainte : ne modifiez jamais `etat` directement, renvoyez un nouveau dictionnaire.''',
            "starter_code": '''def reducer(etat, action):
    ...
''',
            "solution": '''def reducer(etat, action):
    type_action = action.get("type")

    if type_action == "ajouter":
        items = etat["items"] + [{"texte": action["texte"], "fait": False}]
        return {**etat, "items": items}

    if type_action == "basculer":
        index = action["index"]
        items = [
            {**item, "fait": not item["fait"]} if i == index else item
            for i, item in enumerate(etat["items"])
        ]
        return {**etat, "items": items}

    if type_action == "filtrer":
        return {**etat, "filtre": action["valeur"]}

    return etat
''',
            "hints": [
                "`{**etat, \"items\": nouveaux}` crée une copie dont un champ est remplacé.",
                "Pour basculer, reconstruisez la liste avec `enumerate` plutôt que d'écrire `items[i][...] = ...`.",
                "Pour un type inconnu, renvoyez l'objet `etat` lui-même.",
            ],
            "spec": {"tests": [
                {"name": "ajouter", "code": "e = reducer({'items': [], 'filtre': 'tous'}, {'type': 'ajouter', 'texte': 'revoir React'})\nassert e['items'] == [{'texte': 'revoir React', 'fait': False}]"},
                {"name": "etat_non_modifie", "code": "depart = {'items': [], 'filtre': 'tous'}\nreducer(depart, {'type': 'ajouter', 'texte': 'x'})\nassert depart['items'] == []"},
                {"name": "basculer", "code": "e = reducer({'items': [{'texte': 'a', 'fait': False}], 'filtre': 'tous'}, {'type': 'basculer', 'index': 0})\nassert e['items'][0]['fait'] is True"},
                {"name": "filtrer", "code": "e = reducer({'items': [], 'filtre': 'tous'}, {'type': 'filtrer', 'valeur': 'faits'})\nassert e['filtre'] == 'faits'"},
                {"name": "type_inconnu", "code": "depart = {'items': [], 'filtre': 'tous'}\nassert reducer(depart, {'type': 'zzz'}) == depart"},
            ]},
        },
        {
            "slug": "quiz-react",
            "title": "Les pièges de React",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Les erreurs que tout le monde commet en débutant.",
            "spec": {"questions": [
                {"id": "1", "question": "`useEffect(() => fetch(url), [])` relance-t-il l'appel quand `url` change ?", "choices": ["Oui", "Non, il faut mettre url dans les dépendances", "Seulement en production", "Oui, si url est un état"], "answer": "Non, il faut mettre url dans les dépendances", "explanation": "Le tableau vide fige la valeur vue au montage."},
                {"id": "2", "question": "Peut-on écrire `items.push(x)` sur un état ?", "choices": ["Oui", "Non : il faut setItems([...items, x])", "Oui, avec useRef", "Oui, si on force un rendu"], "answer": "Non : il faut setItems([...items, x])", "explanation": "React compare les références : modifier le tableau en place ne déclenche aucun rendu."},
                {"id": "3", "question": "Que faire d'une valeur qui se déduit d'un autre état ?", "choices": ["La dupliquer dans un useState", "La calculer pendant le rendu", "La stocker dans le navigateur", "La mettre dans un useEffect"], "answer": "La calculer pendant le rendu", "explanation": "Dupliquer une valeur dérivée, c'est s'exposer à des incohérences."},
                {"id": "4", "question": "Quelle `key` pour une liste qu'on peut réordonner ?", "choices": ["L'index du tableau", "Un identifiant stable de la donnée", "Math.random()", "Le texte affiché"], "answer": "Un identifiant stable de la donnée", "explanation": "L'index change quand l'ordre change, et `Math.random()` change à chaque rendu."},
            ]},
        },
    ],
}
