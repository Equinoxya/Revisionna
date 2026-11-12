COURSE = {
    "slug": "devops-bases",
    "title": "DevOps : les bases",
    "summary": "Culture DevOps, cycle de vie d'une application, Git en équipe, infrastructure décrite par du code et indicateurs de performance.",
    "category": "DevOps",
    "level": "débutant",
    "icon": "Do",
    "lessons": [
        {
            "slug": "culture-et-cycle-de-vie",
            "title": "La culture DevOps et le cycle de vie",
            "duration_min": 20,
            "blocks": [
                {"type": "text", "md": '''Pendant longtemps, deux équipes se sont fait face. Les **développeurs** (*Dev*) sont jugés sur ce qu'ils livrent : ils veulent du changement. Les **exploitants** (*Ops*) sont jugés sur la stabilité : ils se méfient du changement. Résultat : des mises en ligne rares, énormes, risquées, et un « mur » par-dessus lequel on se renvoie les problèmes.

**DevOps** n'est ni un outil ni un métier à part : c'est une **manière de travailler** où la même équipe conçoit, livre et fait tourner son application. « Vous l'avez construit, vous le faites tourner. »'''},
                {"type": "text", "md": '''Le cycle DevOps se dessine comme une boucle sans fin :

| Étape | Question posée | Outils courants |
|---|---|---|
| Planifier | que construit-on ? | tickets, tableau Kanban |
| Coder | comment l'écrit-on ensemble ? | Git, revue de code |
| Construire | le code s'assemble-t-il ? | Docker, npm, pip |
| Tester | fonctionne-t-il ? | pytest, tests de bout en bout |
| Livrer | la version est-elle prête ? | GitHub Actions, registre d'images |
| Déployer | est-elle en ligne ? | Compose, Kubernetes |
| Exploiter | tourne-t-elle bien ? | systemd, sauvegardes |
| Superviser | que nous apprend la production ? | journaux, métriques, alertes |

Ce que la supervision révèle nourrit la planification suivante : la boucle se referme.'''},
                {"type": "text", "md": '''On résume les piliers par l'acronyme **CALMS** :

- **C**ulture : pas de recherche de coupable, on corrige le système, pas la personne ;
- **A**utomatisation : tout geste répété finit dans un script ou un pipeline ;
- **L**ean : de petits lots, livrés souvent, plutôt qu'une énorme version par trimestre ;
- **M**esure : on décide sur des chiffres, pas sur des impressions ;
- **S**haring (partage) : la connaissance et la responsabilité circulent entre Dev et Ops.'''},
                {"type": "callout", "tone": "info", "md": "Livrer **petit et souvent** réduit le risque : une mise en ligne de dix lignes se relit, se teste et s'annule facilement. Une mise en ligne de dix mille lignes, non."},
                {"type": "text", "md": '''Après un incident, on rédige un **post-mortem sans blâme** : la chronologie, la cause, ce qui a limité ou aggravé les dégâts, et surtout les actions pour que cela ne se reproduise pas. Chercher un coupable apprend aux gens à cacher leurs erreurs ; chercher la faille du système apprend à l'équipe à progresser.'''},
                {"type": "quiz", "id": "q1", "question": "Qu'est-ce que DevOps, avant tout ?", "choices": ["Un logiciel à installer", "Une manière de travailler qui rapproche développement et exploitation", "Un poste réservé aux administrateurs système", "Un langage de script"], "answer": "Une manière de travailler qui rapproche développement et exploitation", "explanation": "Les outils viennent ensuite, au service de cette culture."},
                {"type": "quiz", "id": "q2", "question": "Pourquoi livrer de petits changements, souvent ?", "choices": ["Pour occuper la CI", "Parce que chaque changement est plus facile à relire, tester et annuler", "Parce que les grosses versions sont interdites", "Pour multiplier les réunions"], "answer": "Parce que chaque changement est plus facile à relire, tester et annuler", "explanation": "Le risque d'une mise en ligne grandit avec sa taille."},
                {"type": "quiz", "id": "q3", "question": "Quel est le but d'un post-mortem sans blâme ?", "choices": ["Désigner le responsable de la panne", "Comprendre la faille du système et éviter qu'elle se reproduise", "Rassurer la direction", "Supprimer les journaux de l'incident"], "answer": "Comprendre la faille du système et éviter qu'elle se reproduise", "explanation": "On corrige le processus, pas la personne."},
            ],
        },
        {
            "slug": "git-et-travail-en-equipe",
            "title": "Git et le travail en équipe",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''**Git** garde l'historique complet d'un projet sous forme de **commits** : des instantanés, chacun avec un auteur, une date, un message et un lien vers le commit précédent. Trois zones à avoir en tête :

1. le **dossier de travail** : vos fichiers, modifiés ou non ;
2. l'**index** (*staging*) : ce que vous avez choisi de mettre dans le prochain commit (`git add`) ;
3. le **dépôt** : l'historique des commits (`git commit`).'''},
                {"type": "code", "lang": "bash", "code": '''git status                    # où en suis-je ?
git switch -c feat/inscription   # une branche pour ma fonctionnalité
git add app/api/auth.py       # je choisis ce qui part dans le commit
git commit -m "feat(auth): verifier le format de l'e-mail"
git push -u origin feat/inscription

git log --oneline --graph     # l'historique, en résumé
git diff                      # ce que j'ai modifié et pas encore indexé'''},
                {"type": "text", "md": '''Une **branche** n'est qu'une étiquette mobile posée sur un commit : en créer une ne coûte rien. Le flux de travail le plus répandu, le **GitHub Flow** :

1. `main` est toujours déployable ;
2. chaque changement part d'une branche courte ;
3. on ouvre une **pull request** (PR) : la CI s'exécute, un collègue relit ;
4. une fois approuvée et verte, la branche est fusionnée, puis supprimée.

La revue de code n'est pas un contrôle de police : c'est le moment où la connaissance se partage et où un second regard attrape ce que l'auteur ne voit plus.'''},
                {"type": "text", "md": '''Un bon message de commit dit **pourquoi**, pas seulement quoi. La convention *Conventional Commits* donne un préfixe lisible par les humains comme par les outils :

- `feat:` une fonctionnalité ;
- `fix:` une correction ;
- `docs:`, `test:`, `refactor:`, `chore:` pour le reste.

Quand deux branches modifient les mêmes lignes, Git signale un **conflit** : il ne devine pas, c'est à vous de choisir la bonne version, puis de valider.'''},
                {"type": "callout", "tone": "warn", "md": "Un secret poussé dans Git y reste : le supprimer dans un commit suivant ne l'efface pas de l'historique. La seule réponse sûre est de **révoquer** le secret et d'en générer un autre. Mettez `.env` dans `.gitignore` dès le premier jour."},
                {"type": "callout", "tone": "info", "md": "`git revert` crée un nouveau commit qui annule un ancien : l'historique reste intact, c'est la manière propre d'annuler sur une branche partagée. `git push --force` réécrit l'historique des autres : à éviter sur `main`."},
                {"type": "quiz", "id": "q1", "question": "Que fait `git add` ?", "choices": ["Il envoie le code sur GitHub", "Il place des modifications dans l'index, pour le prochain commit", "Il crée une branche", "Il fusionne deux branches"], "answer": "Il place des modifications dans l'index, pour le prochain commit", "explanation": "On choisit ce qui entre dans le commit, puis `git commit` l'enregistre."},
                {"type": "quiz", "id": "q2", "question": "Vous avez poussé une clé d'API par erreur. Que faire en priorité ?", "choices": ["Supprimer le fichier dans un nouveau commit", "Révoquer la clé et en générer une nouvelle", "Rendre le dépôt privé", "Renommer la variable"], "answer": "Révoquer la clé et en générer une nouvelle", "explanation": "La clé reste lisible dans l'historique : elle doit être considérée comme compromise."},
                {"type": "quiz", "id": "q3", "question": "Comment annuler proprement un commit déjà partagé sur main ?", "choices": ["git push --force", "git revert", "Supprimer le dépôt", "git add --undo"], "answer": "git revert", "explanation": "`revert` ajoute un commit inverse sans réécrire l'historique des autres."},
            ],
        },
        {
            "slug": "automatisation-et-infrastructure",
            "title": "Automatiser : infrastructure as code et mesures",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Configurer un serveur à la main pose trois problèmes : personne ne sait exactement ce qui a été fait, c'est impossible à refaire à l'identique, et chaque serveur finit par devenir un cas particulier (un « flocon de neige »).

L'**infrastructure as code** (IaC) répond en décrivant l'infrastructure dans des fichiers texte, versionnés dans Git, relus en pull request, et appliqués par un outil. Deux styles :

- **impératif** : on liste les étapes (« installe nginx, puis copie ce fichier ») ;
- **déclaratif** : on décrit l'**état voulu** (« nginx doit être installé et démarré »), l'outil calcule les actions nécessaires.'''},
                {"type": "code", "lang": "yaml", "code": '''# Ansible : un playbook déclaratif
- hosts: web
  become: true
  tasks:
    - name: nginx est installé
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: nginx est démarré, y compris après un redémarrage
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true'''},
                {"type": "text", "md": '''La propriété clé est l'**idempotence** : appliquer la même description une fois ou dix fois donne le même résultat. La première exécution installe nginx ; les suivantes constatent qu'il est déjà là et ne font rien.

| Outil | Rôle |
|---|---|
| Terraform, OpenTofu | créer les ressources (machines, réseaux, bases) |
| Ansible | configurer les machines |
| Docker, Compose | empaqueter et lancer l'application |
| Kubernetes | orchestrer des conteneurs sur plusieurs machines |'''},
                {"type": "text", "md": '''On garde plusieurs **environnements** aussi semblables que possible : *développement* (votre poste), *recette* ou *staging* (une copie de la production pour valider), *production* (les vrais utilisateurs). Ce qui change de l'un à l'autre tient dans la **configuration**, jamais dans le code.

Pour savoir si une équipe progresse, on suit les quatre indicateurs **DORA** :

- la **fréquence de déploiement** ;
- le **délai de livraison** : du commit à la production ;
- le **taux d'échec des changements** : la part des déploiements qui provoquent un incident ;
- le **temps de rétablissement** après un incident.

Les deux premiers mesurent la vitesse, les deux derniers la stabilité. Les bonnes équipes progressent sur les quatre à la fois : aller vite et rester stable ne s'opposent pas.'''},
                {"type": "callout", "tone": "warn", "md": "Une modification faite à la main sur un serveur géré par du code crée une **dérive** : la réalité ne correspond plus à la description, et le prochain passage de l'outil l'écrasera. On corrige le code, puis on l'applique."},
                {"type": "quiz", "id": "q1", "question": "Que signifie « idempotent » ?", "choices": ["Qui s'exécute très vite", "Qui donne le même résultat, qu'on l'applique une ou plusieurs fois", "Qui ne peut s'exécuter qu'une seule fois", "Qui ne nécessite aucun droit"], "answer": "Qui donne le même résultat, qu'on l'applique une ou plusieurs fois", "explanation": "On peut relancer l'outil sans crainte : il ne fait que le nécessaire."},
                {"type": "quiz", "id": "q2", "question": "Quel est l'intérêt de décrire l'infrastructure dans Git ?", "choices": ["Aucun, c'est plus long", "Historique, relecture et reproduction à l'identique", "Les serveurs deviennent plus rapides", "On n'a plus besoin de sauvegardes"], "answer": "Historique, relecture et reproduction à l'identique", "explanation": "L'infrastructure profite des mêmes pratiques que le code."},
                {"type": "quiz", "id": "q3", "question": "Quel indicateur DORA mesure la stabilité ?", "choices": ["La fréquence de déploiement", "Le taux d'échec des changements", "Le nombre de lignes de code", "Le nombre de développeurs"], "answer": "Le taux d'échec des changements", "explanation": "Avec le temps de rétablissement, il mesure la stabilité ; les deux autres mesurent la vitesse."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-etat-desire",
            "title": "Converger vers l'état voulu",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Un outil déclaratif compare l'**état actuel** d'une machine à l'**état voulu**, et n'exécute que les actions nécessaires.

Écrivez `planifier(actuel, voulu)`. Les deux arguments sont des dictionnaires `{paquet: version}`. La fonction renvoie une liste d'actions, triée par nom de paquet :

- `("installer", paquet, version)` si le paquet manque ;
- `("mettre_a_jour", paquet, version)` si la version diffère ;
- `("supprimer", paquet, None)` si le paquet est installé mais n'est plus voulu.

Un paquet déjà dans la bonne version ne produit **aucune** action : c'est l'idempotence.''',
            "starter_code": '''def planifier(actuel, voulu):
    ...
''',
            "solution": '''def planifier(actuel, voulu):
    actions = []
    for paquet in sorted(set(actuel) | set(voulu)):
        if paquet not in voulu:
            actions.append(("supprimer", paquet, None))
        elif paquet not in actuel:
            actions.append(("installer", paquet, voulu[paquet]))
        elif actuel[paquet] != voulu[paquet]:
            actions.append(("mettre_a_jour", paquet, voulu[paquet]))
    return actions
''',
            "hints": [
                "Parcourez l'union des clés des deux dictionnaires, triée.",
                "Trois cas : absent de `voulu`, absent de `actuel`, ou versions différentes.",
                "Si rien ne diffère, la liste renvoyée est vide.",
            ],
            "spec": {"tests": [
                {"name": "installation", "code": "assert planifier({}, {'nginx': '1.26'}) == [('installer', 'nginx', '1.26')]"},
                {"name": "mise_a_jour", "code": "assert planifier({'nginx': '1.24'}, {'nginx': '1.26'}) == [('mettre_a_jour', 'nginx', '1.26')]"},
                {"name": "suppression", "code": "assert planifier({'telnet': '0.17'}, {}) == [('supprimer', 'telnet', None)]"},
                {"name": "idempotence", "code": "etat = {'nginx': '1.26', 'git': '2.45'}\nassert planifier(etat, dict(etat)) == []"},
                {"name": "ordre_alphabetique", "code": "plan = planifier({'zsh': '5', 'curl': '8'}, {'curl': '8', 'git': '2', 'ansible': '10'})\nassert plan == [('installer', 'ansible', '10'), ('installer', 'git', '2'), ('supprimer', 'zsh', None)]"},
            ]},
        },
        {
            "slug": "tp-indicateurs-dora",
            "title": "Calculer les indicateurs DORA",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''On vous donne la liste des déploiements d'une période. Chaque déploiement est un dictionnaire :

```python
{"delai_h": 6, "echec": False, "retablissement_min": 0}
```

- `delai_h` : heures écoulées entre le commit et la mise en production ;
- `echec` : le déploiement a-t-il provoqué un incident ?
- `retablissement_min` : minutes pour rétablir le service (0 s'il n'y a pas eu d'échec).

Écrivez `indicateurs(deploiements, jours)`, qui renvoie un dictionnaire :

- `"frequence"` : nombre de déploiements par jour ;
- `"delai_moyen_h"` : délai de livraison moyen ;
- `"taux_echec"` : part des déploiements en échec, entre 0 et 1 ;
- `"retablissement_moyen_min"` : moyenne calculée **sur les seuls échecs** (0 s'il n'y en a aucun).

Arrondissez chaque valeur à 2 décimales. Sans aucun déploiement, toutes les valeurs valent 0.''',
            "starter_code": '''def indicateurs(deploiements, jours):
    ...
''',
            "solution": '''def indicateurs(deploiements, jours):
    total = len(deploiements)
    if total == 0:
        return {"frequence": 0, "delai_moyen_h": 0, "taux_echec": 0, "retablissement_moyen_min": 0}

    echecs = [d for d in deploiements if d["echec"]]
    retablissement = 0
    if echecs:
        retablissement = sum(d["retablissement_min"] for d in echecs) / len(echecs)

    return {
        "frequence": round(total / jours, 2),
        "delai_moyen_h": round(sum(d["delai_h"] for d in deploiements) / total, 2),
        "taux_echec": round(len(echecs) / total, 2),
        "retablissement_moyen_min": round(retablissement, 2),
    }
''',
            "hints": [
                "Traitez d'abord le cas de la liste vide.",
                "Isolez les déploiements en échec dans une liste à part.",
                "Le temps de rétablissement se moyenne sur les échecs, pas sur tous les déploiements.",
            ],
            "spec": {"tests": [
                {"name": "aucun_deploiement", "code": "assert indicateurs([], 7) == {'frequence': 0, 'delai_moyen_h': 0, 'taux_echec': 0, 'retablissement_moyen_min': 0}"},
                {"name": "frequence", "code": "d = [{'delai_h': 2, 'echec': False, 'retablissement_min': 0}] * 14\nassert indicateurs(d, 7)['frequence'] == 2"},
                {"name": "delai_moyen", "code": "d = [{'delai_h': 2, 'echec': False, 'retablissement_min': 0}, {'delai_h': 5, 'echec': False, 'retablissement_min': 0}]\nassert indicateurs(d, 1)['delai_moyen_h'] == 3.5"},
                {"name": "taux_echec", "code": "d = [{'delai_h': 1, 'echec': True, 'retablissement_min': 30}] + [{'delai_h': 1, 'echec': False, 'retablissement_min': 0}] * 3\nassert indicateurs(d, 4)['taux_echec'] == 0.25"},
                {"name": "retablissement_sur_les_echecs", "code": "d = [{'delai_h': 1, 'echec': True, 'retablissement_min': 30}, {'delai_h': 1, 'echec': True, 'retablissement_min': 90}, {'delai_h': 1, 'echec': False, 'retablissement_min': 0}]\nr = indicateurs(d, 3)\nassert r['retablissement_moyen_min'] == 60 and r['taux_echec'] == 0.67"},
            ]},
        },
        {
            "slug": "quiz-devops",
            "title": "Les réflexes DevOps",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Le vocabulaire et les bons réflexes, avant d'attaquer Docker et la CI/CD.",
            "spec": {"questions": [
                {"id": "1", "question": "Dans le GitHub Flow, que doit toujours rester la branche main ?", "choices": ["Vide", "Déployable", "Protégée en lecture", "En avance sur la production"], "answer": "Déployable", "explanation": "Tout ce qui est fusionné dans `main` doit pouvoir partir en production."},
                {"id": "2", "question": "Quel préfixe de commit pour une correction de bug ?", "choices": ["feat:", "fix:", "docs:", "chore:"], "answer": "fix:", "explanation": "`feat:` annonce une fonctionnalité, `fix:` une correction."},
                {"id": "3", "question": "Qu'appelle-t-on un serveur « flocon de neige » ?", "choices": ["Un serveur refroidi", "Un serveur configuré à la main, impossible à reproduire", "Un serveur de sauvegarde", "Un serveur éteint l'hiver"], "answer": "Un serveur configuré à la main, impossible à reproduire", "explanation": "L'infrastructure as code évite ces cas particuliers."},
                {"id": "4", "question": "Qu'est-ce qui doit différer entre la recette et la production ?", "choices": ["Le code", "La configuration seulement", "Le langage", "La version des dépendances"], "answer": "La configuration seulement", "explanation": "Même code, même image : seule la configuration change."},
                {"id": "5", "question": "Que mesure le délai de livraison (lead time) ?", "choices": ["La durée d'une réunion", "Le temps entre le commit et la mise en production", "La durée de la panne", "Le temps d'exécution des tests"], "answer": "Le temps entre le commit et la mise en production", "explanation": "C'est l'un des deux indicateurs DORA de vitesse."},
                {"id": "6", "question": "Vous corrigez un fichier à la main sur un serveur géré par Ansible. Que se passe-t-il au prochain passage de l'outil ?", "choices": ["Rien", "Votre correction est écrasée par l'état décrit dans le code", "Ansible refuse de s'exécuter", "Le serveur redémarre"], "answer": "Votre correction est écrasée par l'état décrit dans le code", "explanation": "C'est la dérive : on corrige toujours la description, pas la machine."},
                {"id": "7", "question": "Que signifie le A de CALMS ?", "choices": ["Architecture", "Automatisation", "Agilité", "Audit"], "answer": "Automatisation", "explanation": "Culture, Automatisation, Lean, Mesure, Sharing."},
                {"id": "8", "question": "Quel outil sert d'abord à créer des ressources (machines, réseaux) ?", "choices": ["Terraform", "pytest", "nginx", "Git"], "answer": "Terraform", "explanation": "Terraform crée les ressources, Ansible les configure."},
            ]},
        },
    ],
}
