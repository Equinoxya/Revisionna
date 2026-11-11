COURSE = {
    "slug": "integration-ia",
    "title": "Intégration de l'IA : Ollama et OpenAI",
    "summary": "Appeler un modèle de langage local ou distant, rédiger un prompt, gérer le coût, la latence, les pannes et la transparence.",
    "category": "IA",
    "level": "intermédiaire",
    "icon": "IA",
    "lessons": [
        {
            "slug": "local-ou-api",
            "title": "Modèle local (Ollama) ou API (OpenAI) ?",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''| Critère | Ollama (local) | OpenAI (API) |
|---|---|---|
| Coût | le matériel, puis rien | à l'usage |
| Données | restent sur la machine | sortent du réseau |
| Qualité | correcte, selon le modèle | généralement supérieure |
| Hors ligne | oui | non |
| Montée en charge | limitée par la carte graphique | élastique |

Le réflexe d'architecture : **une seule interface** dans votre code, deux implémentations derrière.'''},
                {"type": "code", "lang": "python", "code": '''# Ollama : une API HTTP locale, sans clé
requests.post("http://localhost:11434/api/chat", json={
    "model": "llama3.2",
    "stream": False,
    "messages": [
        {"role": "system", "content": "Tu es un tuteur. Donne un indice, pas la solution."},
        {"role": "user", "content": question},
    ],
}, timeout=30).json()["message"]["content"]'''},
                {"type": "code", "lang": "python", "code": '''# OpenAI : la même structure de messages, plus une clé en en-tête
requests.post("https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {cle}"},
    json={"model": "gpt-4o-mini", "temperature": 0.3, "messages": messages},
    timeout=30).json()["choices"][0]["message"]["content"]'''},
                {"type": "callout", "tone": "warn", "md": "Une clé d'API ne va **jamais** dans le code ni dans le dépôt : variable d'environnement ou gestionnaire de secrets. Et jamais dans le navigateur : l'appel passe toujours par votre serveur."},
                {"type": "text", "md": "Voyez `backend/app/services/ai.py` : la fonction `ask()` choisit le fournisseur d'après `AI_PROVIDER`, et un **repli hors ligne** garantit que l'application reste utilisable sans aucun modèle."},
                {"type": "quiz", "id": "q1", "question": "Où ranger OPENAI_API_KEY ?", "choices": ["Dans le code source", "Dans une variable d'environnement, côté serveur", "Dans le stockage local du navigateur", "Dans le dépôt Git"], "answer": "Dans une variable d'environnement, côté serveur", "explanation": "Une clé qui arrive jusqu'au navigateur est une clé compromise."},
                {"type": "quiz", "id": "q2", "question": "Que produit un paramètre `temperature` faible (0,1) ?", "choices": ["Des réponses plus prévisibles", "Des réponses plus créatives", "Des réponses plus longues", "Des appels plus rapides"], "answer": "Des réponses plus prévisibles", "explanation": "La température règle la part de hasard dans le choix des mots."},
            ],
        },
        {
            "slug": "prompts-et-robustesse",
            "title": "Prompts, garde-fous et transparence",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Un prompt efficace précise le **rôle**, la **tâche**, les **contraintes** et le **format** attendu.

> Tu es un tuteur de programmation. Donne un seul indice, en quatre phrases au plus, sans écrire le code final. Réponds en français.

C'est, à peu de chose près, la consigne système de cette application.'''},
                {"type": "text", "md": "Un modèle de langage est un service réseau comme un autre : il lui faut un **délai d'expiration**, un **repli**, et jamais d'exception non gérée qui ferait échouer la requête de l'utilisateur."},
                {"type": "code", "lang": "python", "code": '''try:
    reponse = ask(prompt)
except AIUnavailable:
    reponse = {"provider": "secours", "answer": indice_redige_a_l_avance}'''},
                {"type": "text", "md": "Le **RAG** (*Retrieval Augmented Generation*) tient en trois étapes : découper les documents, retrouver les passages utiles à la question, les glisser dans le prompt. La qualité dépend d'abord de la recherche, pas du modèle."},
                {"type": "callout", "tone": "warn", "md": "Trois obligations dès qu'une IA s'adresse à vos utilisateurs : **dire** que c'est une IA (le règlement européen sur l'IA l'impose), **prévenir** quand leurs données partent chez un tiers, et **ne jamais** injecter sa réponse telle quelle dans une requête SQL ou un `eval`."},
                {"type": "quiz", "id": "q1", "question": "Que signifie RAG ?", "choices": ["Random Answer Generation", "Retrieval Augmented Generation", "Recursive AI Gateway", "Rapid Agent Graph"], "answer": "Retrieval Augmented Generation", "explanation": "On enrichit le prompt avec des documents retrouvés pour l'occasion."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-selection-fournisseur",
            "title": "Choisir le fournisseur d'IA",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Reproduisez la logique de `services/ai.py`.

`choisir_fournisseur(config)` reçoit un dictionnaire et renvoie le nom du fournisseur à utiliser :

- `"openai"` si `config["provider"]` vaut `"openai"` **et** que `config.get("openai_key")` n'est pas vide ;
- `"ollama"` si `config["provider"]` vaut `"ollama"` **et** que `config.get("ollama_url")` n'est pas vide ;
- `"offline"` dans tous les autres cas (fournisseur absent, inconnu, ou configuration incomplète).

La comparaison du nom ne tient compte ni de la casse ni des espaces autour.

Puis `construire_messages(systeme, question, historique=None)` renvoie la liste de messages au format d'une conversation : le message système, puis l'historique tel quel, puis `{"role": "user", "content": question}`.''',
            "starter_code": '''def choisir_fournisseur(config):
    ...


def construire_messages(systeme, question, historique=None):
    ...
''',
            "solution": '''def choisir_fournisseur(config):
    nom = (config.get("provider") or "").strip().lower()
    if nom == "openai" and config.get("openai_key"):
        return "openai"
    if nom == "ollama" and config.get("ollama_url"):
        return "ollama"
    return "offline"


def construire_messages(systeme, question, historique=None):
    messages = [{"role": "system", "content": systeme}]
    messages.extend(historique or [])
    messages.append({"role": "user", "content": question})
    return messages
''',
            "hints": [
                "`(config.get('provider') or '').strip().lower()` règle d'un coup l'absence de clé, la casse et les espaces.",
                "Une chaîne vide vaut faux : `if config.get('openai_key')` suffit.",
                "`historique or []` évite le piège de la valeur par défaut modifiable.",
            ],
            "spec": {"tests": [
                {"name": "openai_configure", "code": "assert choisir_fournisseur({'provider': 'openai', 'openai_key': 'sk-x'}) == 'openai'"},
                {"name": "openai_sans_cle", "code": "assert choisir_fournisseur({'provider': 'openai', 'openai_key': ''}) == 'offline'"},
                {"name": "ollama_casse", "code": "assert choisir_fournisseur({'provider': ' Ollama ', 'ollama_url': 'http://x'}) == 'ollama'"},
                {"name": "config_vide", "code": "assert choisir_fournisseur({}) == 'offline'"},
                {"name": "messages", "code": "m = construire_messages('sys', 'q')\nassert m == [{'role': 'system', 'content': 'sys'}, {'role': 'user', 'content': 'q'}]"},
                {"name": "messages_avec_historique", "code": "h = [{'role': 'user', 'content': 'avant'}, {'role': 'assistant', 'content': 'ok'}]\nm = construire_messages('sys', 'q', h)\nassert len(m) == 4 and m[-1]['content'] == 'q'"},
            ]},
        },
        {
            "slug": "tp-recherche-contexte",
            "title": "Le R de RAG : retrouver le contexte",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Avant d'appeler un modèle, il faut retrouver les passages utiles.

Écrivez `rechercher(documents, question, k=2)` :

- `documents` est une liste de chaînes, `question` une chaîne ;
- le score d'un document est le **nombre de mots de la question qu'il contient** (comparaison en minuscules, mots séparés par des espaces, un mot répété dans la question ne compte qu'une fois) ;
- renvoyez les `k` documents de meilleur score, du plus élevé au plus faible ; à score égal, l'ordre d'origine est conservé ;
- les documents de score nul sont écartés.''',
            "starter_code": '''def rechercher(documents, question, k=2):
    ...
''',
            "solution": '''def rechercher(documents, question, k=2):
    mots = {m for m in question.lower().split() if m}
    scores = []
    for index, doc in enumerate(documents):
        contenu = set(doc.lower().split())
        score = len(mots & contenu)
        if score:
            scores.append((score, index, doc))
    scores.sort(key=lambda item: (-item[0], item[1]))
    return [doc for _, _, doc in scores[:k]]
''',
            "hints": [
                "Transformez la question en `set` de mots pour éliminer les doublons.",
                "`len(mots_question & mots_document)` donne directement le score.",
                "Pour conserver l'ordre d'origine à score égal, triez sur `(-score, index)`.",
            ],
            "spec": {"tests": [
                {"name": "pertinence", "code": "docs = ['les index accelerent les lectures', 'docker construit des images', 'react gere l etat']\nassert rechercher(docs, 'index lectures') == ['les index accelerent les lectures']"},
                {"name": "limite_k", "code": "docs = ['a b', 'b c', 'c d']\nassert len(rechercher(docs, 'b c', k=2)) == 2"},
                {"name": "score_nul_ecarte", "code": "docs = ['rien a voir']\nassert rechercher(docs, 'docker kubernetes') == []"},
                {"name": "casse", "code": "docs = ['Docker Compose orchestre']\nassert rechercher(docs, 'docker') == ['Docker Compose orchestre']"},
                {"name": "ordre_stable", "code": "docs = ['x a', 'y a']\nassert rechercher(docs, 'a', k=2) == ['x a', 'y a']"},
            ]},
        },
    ],
}
