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
                {"type": "quiz", "id": "q2", "question": "À quoi sert la fonction renvoyée par un useEffect ?", "choices": ["À relancer l'effet", "À nettoyer : annuler un abonnement, une minuterie, une requête", "À mettre à jour l'état", "À afficher le composant"], "answer": "À nettoyer : annuler un abonnement, une minuterie, une requête", "explanation": "Elle s'exécute avant l'effet suivant et quand le composant disparaît."},
                {"type": "quiz", "id": "q3", "question": "Qu'est-ce qu'un hook personnalisé ?", "choices": ["Un composant sans JSX", "Une fonction dont le nom commence par use et qui appelle d'autres hooks", "Une classe React", "Un fichier de configuration"], "answer": "Une fonction dont le nom commence par use et qui appelle d'autres hooks", "explanation": "Il permet de partager une logique entre plusieurs composants."},
            ],
        },
        {
            "slug": "formulaires-routage-et-contexte",
            "title": "Formulaires, routage et état partagé",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Dans un **formulaire contrôlé**, c'est l'état React qui fait foi : chaque champ affiche une valeur de l'état (`value`) et la met à jour à chaque frappe (`onChange`). On peut alors valider, désactiver un bouton ou afficher une erreur à tout moment.'''},
                {"type": "code", "lang": "jsx", "code": '''function Connexion({ onConnexion }) {
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  async function envoyer(evenement) {
    evenement.preventDefault();            // pas de rechargement de la page
    setEnvoi(true);
    setErreur(null);
    try {
      await onConnexion({ email, motDePasse });
    } catch (exception) {
      setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  return (
    <form onSubmit={envoyer}>
      <label>
        E-mail
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label>
        Mot de passe
        <input type="password" value={motDePasse} onChange={(e) => setMotDePasse(e.target.value)} required />
      </label>
      {erreur && <p role="alert">{erreur}</p>}
      <button disabled={envoi}>{envoi ? "Connexion…" : "Se connecter"}</button>
    </form>
  );
}'''},
                {"type": "callout", "tone": "info", "md": "Un appel réseau a toujours **trois états** : en cours, réussi, en échec. Une interface qui n'en gère qu'un seul laisse l'utilisateur devant un écran figé ou un bouton sur lequel il clique dix fois."},
                {"type": "text", "md": '''Une application React ne recharge jamais la page : c'est le **routeur** qui affiche le bon composant selon l'URL. Avec React Router :'''},
                {"type": "code", "lang": "jsx", "code": '''<BrowserRouter>
  <Routes>
    <Route path="/" element={<Sommaire />} />
    <Route path="/cours/:slug" element={<Cours />} />
    <Route path="*" element={<Introuvable />} />
  </Routes>
</BrowserRouter>

function Cours() {
  const { slug } = useParams();              // la partie variable de l'URL
  const naviguer = useNavigate();            // changer de page depuis le code
  return <Link to="/">Retour au sommaire</Link>;   // jamais <a href> en interne
}'''},
                {"type": "text", "md": '''Quand deux composants ont besoin de la même donnée, on la **remonte** dans leur parent commun, qui la redistribue par les props. Quand la donnée concerne toute l'application (l'utilisateur connecté, le thème), la faire descendre de composant en composant devient pénible. Le **contexte** la rend disponible partout, sans intermédiaire.'''},
                {"type": "code", "lang": "jsx", "code": '''const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [utilisateur, setUtilisateur] = useState(null);
  return (
    <AuthContext.Provider value={{ utilisateur, setUtilisateur }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

// n'importe où dans l'arbre :
function EnTete() {
  const { utilisateur } = useAuth();
  return <span>{utilisateur ? utilisateur.nom : "Invité"}</span>;
}'''},
                {"type": "text", "md": "C'est le fonctionnement de cette application : `frontend/src/lib/AuthContext.jsx` garde l'utilisateur connecté, et `ProtectedRoute.jsx` redirige vers la connexion quand il n'y en a pas."},
                {"type": "callout", "tone": "warn", "md": "Masquer un bouton dans l'interface n'est pas une protection : tout le code du frontend est lisible et modifiable par l'utilisateur. Les droits se vérifient **côté serveur**, à chaque requête."},
                {"type": "quiz", "id": "q1", "question": "Dans un champ contrôlé, d'où vient la valeur affichée ?", "choices": ["Du DOM", "De l'état React", "Du serveur", "Du localStorage"], "answer": "De l'état React", "explanation": "`value` lit l'état, `onChange` le met à jour."},
                {"type": "quiz", "id": "q2", "question": "Pourquoi appeler `preventDefault()` à l'envoi d'un formulaire ?", "choices": ["Pour vider les champs", "Pour empêcher le navigateur de recharger la page", "Pour valider les champs", "Pour chiffrer les données"], "answer": "Pour empêcher le navigateur de recharger la page", "explanation": "On traite l'envoi nous-mêmes, avec un appel réseau."},
                {"type": "quiz", "id": "q3", "question": "Quand utiliser un contexte ?", "choices": ["Pour chaque état", "Pour une donnée utile à toute l'application, comme l'utilisateur connecté", "Pour remplacer les props partout", "Jamais"], "answer": "Pour une donnée utile à toute l'application, comme l'utilisateur connecté", "explanation": "Pour un état local, `useState` et les props restent plus simples."},
                {"type": "quiz", "id": "q4", "question": "Un bouton réservé aux administrateurs est masqué dans l'interface. Est-ce suffisant ?", "choices": ["Oui", "Non : le serveur doit vérifier les droits à chaque requête", "Oui, si le code est minifié", "Oui, avec un contexte"], "answer": "Non : le serveur doit vérifier les droits à chaque requête", "explanation": "Le frontend s'exécute chez l'utilisateur, qui peut le contourner."},
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
                {"id": "5", "question": "Comment un enfant prévient-il son parent d'un événement ?", "choices": ["En modifiant les props", "En appelant une fonction reçue en prop", "En modifiant l'état du parent directement", "C'est impossible"], "answer": "En appelant une fonction reçue en prop", "explanation": "Les données descendent par les props, les événements remontent par des fonctions."},
                {"id": "6", "question": "Un composant peut-il modifier ses props ?", "choices": ["Oui", "Non, elles sont en lecture seule", "Seulement dans un effet", "Seulement avec useState"], "answer": "Non, elles sont en lecture seule", "explanation": "Seul le parent, qui les fournit, peut les changer."},
                {"id": "7", "question": "Quel composant utiliser pour un lien interne avec React Router ?", "choices": ["<a href>", "<Link to>", "<button>", "<Route>"], "answer": "<Link to>", "explanation": "`<a href>` recharge toute la page et fait perdre l'état de l'application."},
                {"id": "8", "question": "Que provoque `setValeur(valeur)` avec une valeur identique à l'actuelle ?", "choices": ["Un nouvel affichage complet", "Rien : React ignore la mise à jour", "Une erreur", "Une boucle infinie"], "answer": "Rien : React ignore la mise à jour", "explanation": "React compare l'ancienne et la nouvelle valeur avant de réafficher."},
            ]},
        },
    ],
}
