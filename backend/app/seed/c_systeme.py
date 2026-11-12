COURSE = {
    "slug": "systeme-linux",
    "title": "Système : Linux et la ligne de commande",
    "summary": "Arborescence, shell, utilisateurs et permissions, processus, services systemd, journaux, paquets et scripts.",
    "category": "Système et réseaux",
    "level": "débutant",
    "icon": "Sy",
    "lessons": [
        {
            "slug": "shell-et-arborescence",
            "title": "Le shell et l'arborescence",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''La grande majorité des serveurs tournent sous **Linux**, et on les administre sans interface graphique, depuis un **shell** (le plus souvent `bash`). Le shell lit une commande, l'exécute, affiche le résultat, et recommence.

Sous Linux, **tout est fichier**, rangé dans une arborescence unique qui part de la racine `/` :

| Dossier | Contenu |
|---|---|
| `/home` | les dossiers personnels des utilisateurs |
| `/etc` | la configuration du système et des services |
| `/var` | ce qui grossit : journaux (`/var/log`), données |
| `/usr`, `/bin` | les programmes |
| `/tmp` | les fichiers temporaires, effacés au redémarrage |
| `/root` | le dossier personnel de l'administrateur |'''},
                {"type": "code", "lang": "bash", "code": '''pwd                      # où suis-je ?
ls -la /etc              # liste détaillée, fichiers cachés compris
cd /var/log              # changer de dossier ; cd ~ ramène chez soi
mkdir -p projet/src      # créer un dossier et ses parents
cp -r projet sauvegarde  # copier (-r pour un dossier)
mv ancien.txt nouveau.txt   # déplacer ou renommer
rm -r sauvegarde         # supprimer : il n'y a pas de corbeille

cat /etc/hostname        # afficher un fichier
less /var/log/syslog     # le parcourir page par page (q pour quitter)
tail -f /var/log/syslog  # suivre les nouvelles lignes en direct
man ls                   # le manuel d'une commande'''},
                {"type": "text", "md": '''Un chemin **absolu** part de la racine (`/etc/nginx/nginx.conf`) ; un chemin **relatif** part du dossier courant (`src/app.py`). `.` désigne le dossier courant, `..` le dossier parent, `~` votre dossier personnel.

La force du shell tient aux **redirections** et aux **tubes** : chaque commande fait une seule chose, et on les enchaîne.

- `>` écrit la sortie dans un fichier (en l'écrasant), `>>` ajoute à la fin ;
- `|` envoie la sortie d'une commande à l'entrée de la suivante ;
- `2>` redirige les erreurs.'''},
                {"type": "code", "lang": "bash", "code": '''# les 5 adresses IP qui reviennent le plus dans un journal nginx
cut -d' ' -f1 /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -5

grep -rn "ERROR" /var/log/app/        # chercher un texte dans des fichiers
find /var/log -name "*.log" -mtime +7  # les .log modifiés il y a plus de 7 jours
wc -l fichier.txt                      # compter les lignes'''},
                {"type": "callout", "tone": "warn", "md": "`rm -rf` supprime sans confirmation et sans corbeille. Relisez toujours le chemin avant d'appuyer sur Entrée, surtout s'il contient une variable : `rm -rf \"$DOSSIER\"/` avec une variable vide devient `rm -rf /`."},
                {"type": "quiz", "id": "q1", "question": "Dans quel dossier trouve-t-on la configuration des services ?", "choices": ["/home", "/etc", "/tmp", "/var/log"], "answer": "/etc", "explanation": "`/etc` regroupe la configuration ; `/var/log` contient les journaux."},
                {"type": "quiz", "id": "q2", "question": "Que fait le symbole | entre deux commandes ?", "choices": ["Il lance les deux en parallèle", "Il envoie la sortie de la première à l'entrée de la seconde", "Il écrit dans un fichier", "Il exécute la seconde si la première échoue"], "answer": "Il envoie la sortie de la première à l'entrée de la seconde", "explanation": "C'est le tube (*pipe*) : il permet de composer de petites commandes."},
                {"type": "quiz", "id": "q3", "question": "Quelle différence entre > et >> ?", "choices": ["Aucune", "> écrase le fichier, >> ajoute à la fin", "> ajoute, >> écrase", ">> redirige les erreurs"], "answer": "> écrase le fichier, >> ajoute à la fin", "explanation": "Un `>` de trop sur un fichier de configuration le vide."},
            ],
        },
        {
            "slug": "utilisateurs-et-permissions",
            "title": "Utilisateurs, groupes et permissions",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Linux est **multi-utilisateur**. Chaque fichier appartient à un **propriétaire** et à un **groupe**, et porte trois séries de droits : pour le propriétaire (`u`), pour le groupe (`g`), pour tous les autres (`o`).

Trois droits possibles :

| Droit | Sur un fichier | Sur un dossier |
|---|---|---|
| `r` (lecture) | lire le contenu | lister les fichiers |
| `w` (écriture) | modifier le contenu | créer et supprimer des fichiers |
| `x` (exécution) | lancer le fichier comme un programme | entrer dans le dossier |'''},
                {"type": "code", "lang": "bash", "code": '''$ ls -l deploy.sh
-rwxr-x--- 1 alice devs 412 12 nov. 09:30 deploy.sh
#│└┬┘└┬┘└┬┘   └─┬─┘ └┬─┘
#│ │  │  │      │    └ groupe
#│ │  │  │      └ propriétaire
#│ │  │  └ les autres : aucun droit
#│ │  └ le groupe devs : lire et exécuter
#│ └ alice : lire, écrire, exécuter
#└ type : - fichier, d dossier, l lien'''},
                {"type": "text", "md": '''Chaque droit vaut un chiffre : **r = 4, w = 2, x = 1**. On les additionne par série : `rwx` = 7, `r-x` = 5, `r--` = 4, `---` = 0. Le fichier ci-dessus est donc en **750**.

Les valeurs à connaître :

- `644` : un fichier ordinaire, lisible par tous, modifiable par son propriétaire ;
- `755` : un script ou un dossier public ;
- `600` : un fichier privé (clé SSH, fichier `.env`) ;
- `700` : un dossier privé.'''},
                {"type": "code", "lang": "bash", "code": '''chmod 600 .env             # notation octale
chmod u+x script.sh        # notation symbolique : ajouter x au propriétaire
chmod -R g-w dossier/      # retirer l'écriture au groupe, récursivement
chown alice:devs fichier   # changer le propriétaire et le groupe

whoami                     # qui suis-je ?
id                         # mon identifiant et mes groupes
sudo adduser bob           # créer un utilisateur
sudo usermod -aG docker bob   # l'ajouter au groupe docker'''},
                {"type": "text", "md": '''L'utilisateur **root** (identifiant 0) a tous les droits : aucune permission ne l'arrête, aucune erreur non plus. On ne travaille donc jamais connecté en root. On utilise **`sudo`**, qui exécute *une* commande avec les droits d'administrateur, après vérification du mot de passe, et en laissant une trace dans les journaux.

C'est le **principe du moindre privilège** : chaque utilisateur, chaque service ne reçoit que les droits dont il a besoin. Un serveur web tourne sous un compte dédié (`www-data`, `nginx`) : s'il est compromis, l'attaquant n'hérite que de ces droits-là.'''},
                {"type": "callout", "tone": "warn", "md": "`chmod 777` « règle » un problème de droits en donnant tout à tout le monde. C'est presque toujours une faille : cherchez plutôt **quel utilisateur** a besoin de **quel droit**, et corrigez le propriétaire ou le groupe."},
                {"type": "quiz", "id": "q1", "question": "Que vaut rw-r--r-- en notation octale ?", "choices": ["755", "644", "600", "664"], "answer": "644", "explanation": "rw- = 4+2 = 6, r-- = 4, r-- = 4."},
                {"type": "quiz", "id": "q2", "question": "Quels droits donner à une clé SSH privée ?", "choices": ["777", "644", "600", "755"], "answer": "600", "explanation": "Lisible et modifiable par son seul propriétaire ; SSH refuse d'ailleurs une clé trop ouverte."},
                {"type": "quiz", "id": "q3", "question": "Pourquoi préférer sudo à une session root ?", "choices": ["C'est plus rapide", "Les droits ne sont élevés que pour une commande, et l'action est journalisée", "root n'existe plus", "sudo ne demande jamais de mot de passe"], "answer": "Les droits ne sont élevés que pour une commande, et l'action est journalisée", "explanation": "Moins de temps passé avec tous les droits, c'est moins d'erreurs irréversibles."},
                {"type": "quiz", "id": "q4", "question": "Que permet le droit x sur un dossier ?", "choices": ["L'exécuter comme un programme", "Y entrer (le traverser)", "Le supprimer", "Le renommer"], "answer": "Y entrer (le traverser)", "explanation": "Sans `x`, on ne peut pas accéder à ce que contient le dossier, même avec `r`."},
            ],
        },
        {
            "slug": "processus-services-et-journaux",
            "title": "Processus, services et journaux",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Un **processus** est un programme en cours d'exécution. Il a un identifiant (**PID**), un propriétaire, un parent, et consomme du processeur et de la mémoire.'''},
                {"type": "code", "lang": "bash", "code": '''ps aux                 # tous les processus
ps aux | grep nginx    # ceux qui concernent nginx
top                    # vue en direct (htop, plus lisible, s'installe à part)

kill 4242              # SIGTERM : demande polie de s'arrêter
kill -9 4242           # SIGKILL : arrêt forcé, sans nettoyage

df -h                  # espace disque par partition
du -sh /var/log/*      # taille de chaque dossier
free -h                # mémoire vive'''},
                {"type": "callout", "tone": "info", "md": "Envoyez toujours `SIGTERM` d'abord : le programme ferme ses fichiers et termine ses requêtes en cours. `kill -9` ne lui laisse aucune chance et peut corrompre des données. C'est le dernier recours."},
                {"type": "text", "md": '''Un **service** (ou *démon*) est un processus qui tourne en arrière-plan : serveur web, base de données, SSH. Sur la plupart des distributions, c'est **systemd** qui les lance, les surveille et les relance.'''},
                {"type": "code", "lang": "bash", "code": '''sudo systemctl status nginx     # état, PID, dernières lignes de journal
sudo systemctl start nginx      # démarrer maintenant
sudo systemctl restart nginx    # redémarrer
sudo systemctl reload nginx     # relire la configuration sans coupure
sudo systemctl enable nginx     # démarrer aussi à chaque redémarrage de la machine

journalctl -u nginx -f          # suivre le journal du service
journalctl -u nginx --since "1 hour ago"
journalctl -p err -b            # les erreurs depuis le dernier démarrage'''},
                {"type": "text", "md": '''`start` et `enable` ne font pas la même chose : `start` agit **maintenant**, `enable` agit **au prochain démarrage**. Un service démarré mais pas activé disparaît au premier redémarrage de la machine.

Les logiciels s'installent avec le **gestionnaire de paquets** de la distribution, qui gère les dépendances et les mises à jour de sécurité : `apt` sur Debian et Ubuntu, `dnf` sur Fedora et Red Hat.'''},
                {"type": "code", "lang": "bash", "code": '''sudo apt update            # rafraîchir la liste des paquets disponibles
sudo apt upgrade           # appliquer les mises à jour
sudo apt install htop      # installer
sudo apt remove htop       # désinstaller'''},
                {"type": "text", "md": '''Tout ce qu'on tape deux fois mérite un **script**. La première ligne (le *shebang*) indique l'interpréteur ; `set -euo pipefail` arrête le script à la première erreur au lieu de continuer sur des bases fausses.'''},
                {"type": "code", "lang": "bash", "code": '''#!/usr/bin/env bash
set -euo pipefail

DESTINATION="/srv/sauvegardes/$(date +%F)"
mkdir -p "$DESTINATION"

for base in app stats; do
    pg_dump "$base" | gzip > "$DESTINATION/$base.sql.gz"
    echo "sauvegarde de $base terminée"
done

# supprimer les sauvegardes de plus de 14 jours
find /srv/sauvegardes -mindepth 1 -maxdepth 1 -mtime +14 -exec rm -r {} +'''},
                {"type": "text", "md": '''Pour l'exécuter tout seul, on le confie à **cron**. `crontab -e` ouvre la table de l'utilisateur ; chaque ligne donne cinq champs, puis la commande :

```
# minute  heure  jour-du-mois  mois  jour-de-la-semaine  commande
  30      2      *             *     *                   /usr/local/bin/sauvegarde.sh
```

Cette ligne lance la sauvegarde tous les jours à 2 h 30. `*/15 * * * *` signifie « toutes les 15 minutes ».'''},
                {"type": "quiz", "id": "q1", "question": "Quelle différence entre `systemctl start` et `systemctl enable` ?", "choices": ["Aucune", "start démarre maintenant, enable démarre à chaque redémarrage de la machine", "enable démarre maintenant, start au redémarrage", "enable installe le service"], "answer": "start démarre maintenant, enable démarre à chaque redémarrage de la machine", "explanation": "On fait souvent les deux : `systemctl enable --now nginx`."},
                {"type": "quiz", "id": "q2", "question": "Pourquoi essayer `kill` avant `kill -9` ?", "choices": ["kill -9 est plus lent", "SIGTERM laisse le programme s'arrêter proprement", "kill -9 exige d'être root", "Il n'y a aucune raison"], "answer": "SIGTERM laisse le programme s'arrêter proprement", "explanation": "SIGKILL coupe net : fichiers non fermés, données possiblement corrompues."},
                {"type": "quiz", "id": "q3", "question": "Que signifie la ligne cron `0 3 * * 1` ?", "choices": ["Toutes les 3 minutes", "Tous les lundis à 3 h", "Le 1er de chaque mois à 3 h", "Tous les jours à 3 h 01"], "answer": "Tous les lundis à 3 h", "explanation": "Minute 0, heure 3, n'importe quel jour du mois, n'importe quel mois, jour de la semaine 1 (lundi)."},
                {"type": "quiz", "id": "q4", "question": "À quoi sert `set -e` en tête d'un script bash ?", "choices": ["À afficher chaque commande", "À arrêter le script dès qu'une commande échoue", "À l'exécuter en root", "À ignorer les erreurs"], "answer": "À arrêter le script dès qu'une commande échoue", "explanation": "Sans lui, le script continue après une erreur, avec des conséquences imprévisibles."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-permissions",
            "title": "Lire les permissions",
            "kind": "python",
            "difficulty": "facile",
            "statement": '''Écrivez deux fonctions de conversion entre les deux notations des permissions Unix.

`en_symbolique(octal)` reçoit une chaîne de trois chiffres et renvoie les neuf caractères correspondants :

```python
en_symbolique("750")  # "rwxr-x---"
```

`en_octal(symbolique)` fait l'inverse :

```python
en_octal("rw-r--r--")  # "644"
```

Rappel : r = 4, w = 2, x = 1.''',
            "starter_code": '''def en_symbolique(octal):
    ...


def en_octal(symbolique):
    ...
''',
            "solution": '''def en_symbolique(octal):
    resultat = ""
    for chiffre in octal:
        valeur = int(chiffre)
        resultat += "r" if valeur & 4 else "-"
        resultat += "w" if valeur & 2 else "-"
        resultat += "x" if valeur & 1 else "-"
    return resultat


def en_octal(symbolique):
    poids = {"r": 4, "w": 2, "x": 1, "-": 0}
    resultat = ""
    for debut in range(0, 9, 3):
        resultat += str(sum(poids[c] for c in symbolique[debut:debut + 3]))
    return resultat
''',
            "hints": [
                "Traitez chaque chiffre séparément : il décrit trois caractères.",
                "Pour savoir si un droit est présent, testez `valeur & 4`, `valeur & 2`, `valeur & 1` (ou soustrayez).",
                "Dans l'autre sens, découpez la chaîne en trois tranches de trois caractères et additionnez les poids.",
            ],
            "spec": {"tests": [
                {"name": "script_750", "code": "assert en_symbolique('750') == 'rwxr-x---'"},
                {"name": "fichier_644", "code": "assert en_symbolique('644') == 'rw-r--r--'"},
                {"name": "aucun_droit", "code": "assert en_symbolique('000') == '---------'"},
                {"name": "vers_octal", "code": "assert en_octal('rw-r--r--') == '644'\nassert en_octal('rwx------') == '700'"},
                {"name": "aller_retour", "code": "for n in ['777', '600', '755', '421', '136']:\n    assert en_octal(en_symbolique(n)) == n"},
            ]},
        },
        {
            "slug": "tp-analyse-journal",
            "title": "Analyser un journal",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Un journal applicatif contient des lignes de la forme :

```
2026-11-12 09:30:01 ERROR api Connexion à la base refusée
```

soit : date, heure, niveau, service, puis le message.

Écrivez `resumer(lignes)`, qui reçoit une liste de lignes et renvoie un dictionnaire :

- `"par_niveau"` : le nombre de lignes par niveau, par exemple `{"INFO": 3, "ERROR": 1}` ;
- `"erreurs_par_service"` : le nombre de lignes `ERROR` par service ;
- `"pire_service"` : le service qui a le plus d'erreurs (`None` s'il n'y en a aucune ; en cas d'égalité, le premier par ordre alphabétique).

Les lignes vides, ou qui ont moins de quatre champs, sont ignorées.''',
            "starter_code": '''def resumer(lignes):
    ...
''',
            "solution": '''def resumer(lignes):
    par_niveau = {}
    erreurs = {}
    for ligne in lignes:
        champs = ligne.split()
        if len(champs) < 4:
            continue
        niveau, service = champs[2], champs[3]
        par_niveau[niveau] = par_niveau.get(niveau, 0) + 1
        if niveau == "ERROR":
            erreurs[service] = erreurs.get(service, 0) + 1

    pire = None
    if erreurs:
        pire = min(erreurs, key=lambda service: (-erreurs[service], service))

    return {"par_niveau": par_niveau, "erreurs_par_service": erreurs, "pire_service": pire}
''',
            "hints": [
                "`ligne.split()` découpe sur les espaces : le niveau est le champ 2, le service le champ 3.",
                "`dictionnaire.get(cle, 0) + 1` compte sans se soucier de la première apparition.",
                "Pour départager les égalités, triez sur le couple `(-nombre, nom)`.",
            ],
            "spec": {"tests": [
                {"name": "comptage_par_niveau", "code": "l = ['2026-11-12 09:00:00 INFO api Démarrage', '2026-11-12 09:00:01 INFO api Prêt', '2026-11-12 09:00:02 ERROR db Refus']\nassert resumer(l)['par_niveau'] == {'INFO': 2, 'ERROR': 1}"},
                {"name": "erreurs_par_service", "code": "l = ['d h ERROR api a', 'd h ERROR db b', 'd h ERROR api c', 'd h INFO api d']\nassert resumer(l)['erreurs_par_service'] == {'api': 2, 'db': 1}"},
                {"name": "pire_service", "code": "l = ['d h ERROR api a', 'd h ERROR db b', 'd h ERROR db c']\nassert resumer(l)['pire_service'] == 'db'"},
                {"name": "aucune_erreur", "code": "r = resumer(['d h INFO api tout va bien'])\nassert r['pire_service'] is None and r['erreurs_par_service'] == {}"},
                {"name": "lignes_invalides_ignorees", "code": "r = resumer(['', 'incomplete', 'd h WARNING web lent'])\nassert r['par_niveau'] == {'WARNING': 1}"},
                {"name": "egalite_alphabetique", "code": "l = ['d h ERROR web a', 'd h ERROR api b']\nassert resumer(l)['pire_service'] == 'api'"},
            ]},
        },
        {
            "slug": "quiz-systeme",
            "title": "Les commandes à connaître",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Ce qu'il faut savoir taper sans réfléchir sur un serveur.",
            "spec": {"questions": [
                {"id": "1", "question": "Quelle commande suit un journal en direct ?", "choices": ["cat fichier", "tail -f fichier", "head fichier", "wc -l fichier"], "answer": "tail -f fichier", "explanation": "`-f` (*follow*) affiche les nouvelles lignes à mesure qu'elles arrivent."},
                {"id": "2", "question": "Le disque est plein. Quelle commande montre l'espace par partition ?", "choices": ["free -h", "df -h", "ps aux", "top"], "answer": "df -h", "explanation": "`df` pour les partitions, `du` pour la taille d'un dossier, `free` pour la mémoire."},
                {"id": "3", "question": "Que fait `chmod u+x script.sh` ?", "choices": ["Il supprime le script", "Il rend le script exécutable par son propriétaire", "Il change le propriétaire", "Il l'exécute"], "answer": "Il rend le script exécutable par son propriétaire", "explanation": "`u` pour le propriétaire, `+x` pour ajouter l'exécution."},
                {"id": "4", "question": "Vous modifiez la configuration de nginx. Comment l'appliquer sans coupure ?", "choices": ["systemctl stop nginx", "systemctl reload nginx", "kill -9 nginx", "reboot"], "answer": "systemctl reload nginx", "explanation": "`reload` relit la configuration sans interrompre les connexions en cours."},
                {"id": "5", "question": "Quelle commande rafraîchit la liste des paquets sous Debian ou Ubuntu ?", "choices": ["apt upgrade", "apt update", "apt install", "apt refresh"], "answer": "apt update", "explanation": "`update` met à jour la liste, `upgrade` installe les nouvelles versions."},
                {"id": "6", "question": "Que désigne `..` dans un chemin ?", "choices": ["Le dossier courant", "Le dossier parent", "La racine", "Le dossier personnel"], "answer": "Le dossier parent", "explanation": "`.` est le dossier courant, `~` le dossier personnel, `/` la racine."},
                {"id": "7", "question": "Où chercher les journaux d'un service géré par systemd ?", "choices": ["journalctl -u service", "ls /etc", "man service", "crontab -l"], "answer": "journalctl -u service", "explanation": "`-u` filtre sur une unité ; ajoutez `-f` pour suivre en direct."},
                {"id": "8", "question": "Sous quel compte faire tourner un serveur web ?", "choices": ["root, pour éviter les problèmes de droits", "Un compte dédié, avec le minimum de droits", "Le compte du dernier développeur connecté", "Peu importe"], "answer": "Un compte dédié, avec le minimum de droits", "explanation": "S'il est compromis, l'attaquant n'obtient que ces droits-là."},
            ]},
        },
    ],
}
