COURSE = {
    "slug": "reseaux",
    "title": "Administration réseaux : les bases",
    "summary": "Modèles en couches, adressage IP et sous-réseaux, DNS, DHCP, ports, routage, NAT, pare-feu, SSH et outils de diagnostic.",
    "category": "Système et réseaux",
    "level": "débutant",
    "icon": "Rx",
    "lessons": [
        {
            "slug": "modeles-et-adressage-ip",
            "title": "Modèles en couches et adressage IP",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Un réseau se découpe en **couches** : chacune rend un service à celle du dessus sans se soucier du détail de celle du dessous. Le modèle théorique, **OSI**, en compte sept ; le modèle réellement utilisé sur Internet, **TCP/IP**, en regroupe quatre.

| TCP/IP | Couches OSI | Rôle | Exemples |
|---|---|---|---|
| Application | 7, 6, 5 | le dialogue entre programmes | HTTP, DNS, SSH |
| Transport | 4 | de bout en bout, entre deux ports | TCP, UDP |
| Internet | 3 | acheminer entre réseaux | IP, ICMP |
| Accès réseau | 2, 1 | le lien physique local | Ethernet, Wi-Fi |

À l'envoi, chaque couche **encapsule** les données de la précédente en y ajoutant son en-tête : la requête HTTP voyage dans un segment TCP, lui-même dans un paquet IP, lui-même dans une trame Ethernet.'''},
                {"type": "text", "md": '''Deux adresses identifient une machine :

- l'adresse **MAC** (couche 2) : gravée dans la carte réseau, valable sur le réseau local seulement ;
- l'adresse **IP** (couche 3) : attribuée, elle permet de joindre la machine depuis un autre réseau.

Une adresse **IPv4** tient sur 32 bits, écrits en quatre nombres de 0 à 255 : `192.168.1.42`. Elle se lit en deux parties : la partie **réseau**, commune à toutes les machines du même réseau, et la partie **hôte**, propre à chacune. C'est le **masque** qui indique où passe la frontière.

La notation **CIDR** donne le nombre de bits de la partie réseau : `192.168.1.42/24` signifie « les 24 premiers bits désignent le réseau », soit le masque `255.255.255.0`.'''},
                {"type": "code", "lang": "text", "code": '''Adresse   192.168.1.42/24

192.168.1 . 42
└───┬───┘   └┬┘
  réseau    hôte

Adresse du réseau     192.168.1.0     (tous les bits d'hôte à 0)
Adresse de diffusion  192.168.1.255   (tous les bits d'hôte à 1)
Hôtes utilisables     192.168.1.1 à 192.168.1.254
Nombre d'hôtes        2^(32-24) - 2 = 254'''},
                {"type": "text", "md": '''Le nombre d'adresses d'un réseau `/n` vaut `2^(32-n)`. On en retire deux, réservées : l'adresse du **réseau** et l'adresse de **diffusion** (*broadcast*), qui s'adresse à toutes les machines à la fois.

| CIDR | Masque | Hôtes utilisables |
|---|---|---|
| /8 | 255.0.0.0 | 16 777 214 |
| /16 | 255.255.0.0 | 65 534 |
| /24 | 255.255.255.0 | 254 |
| /26 | 255.255.255.192 | 62 |
| /30 | 255.255.255.252 | 2 |

Certaines plages sont **privées** : elles ne circulent pas sur Internet et se réutilisent librement dans chaque réseau local.

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

`127.0.0.1` (*localhost*) désigne toujours la machine elle-même.'''},
                {"type": "callout", "tone": "info", "md": "**IPv6** répond à la pénurie d'adresses IPv4 : 128 bits, écrits en hexadécimal (`2001:db8::1`). Les principes restent les mêmes : un préfixe pour le réseau, le reste pour l'hôte."},
                {"type": "quiz", "id": "q1", "question": "Combien d'hôtes utilisables dans un réseau /24 ?", "choices": ["256", "254", "255", "24"], "answer": "254", "explanation": "2^8 = 256 adresses, moins l'adresse du réseau et celle de diffusion."},
                {"type": "quiz", "id": "q2", "question": "Laquelle de ces adresses est privée ?", "choices": ["8.8.8.8", "192.168.10.5", "172.32.0.1", "193.168.1.1"], "answer": "192.168.10.5", "explanation": "Elle appartient à 192.168.0.0/16. Attention : 172.32.x.x sort de la plage privée 172.16.0.0/12."},
                {"type": "quiz", "id": "q3", "question": "À quelle couche travaille le protocole IP ?", "choices": ["Application", "Transport", "Internet (couche 3)", "Accès réseau"], "answer": "Internet (couche 3)", "explanation": "IP achemine les paquets d'un réseau à l'autre ; TCP et UDP sont à la couche transport."},
                {"type": "quiz", "id": "q4", "question": "Quelle est l'adresse de diffusion de 10.0.5.0/24 ?", "choices": ["10.0.5.0", "10.0.5.1", "10.0.5.255", "10.255.255.255"], "answer": "10.0.5.255", "explanation": "Tous les bits de la partie hôte à 1."},
            ],
        },
        {
            "slug": "ports-dns-et-dhcp",
            "title": "Ports, TCP, UDP, DNS et DHCP",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''L'adresse IP désigne une machine ; le **port** désigne un programme sur cette machine. Un service **écoute** sur un port, de 0 à 65535. Ceux à connaître :

| Port | Service |
|---|---|
| 22 | SSH |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 5432 | PostgreSQL |
| 3306 | MySQL |
| 27017 | MongoDB |

Les ports inférieurs à 1024 sont réservés : il faut des droits d'administrateur pour y écouter.'''},
                {"type": "text", "md": '''Deux protocoles de transport :

| | TCP | UDP |
|---|---|---|
| Connexion | oui, établie en trois temps | non |
| Fiabilité | accusés de réception, retransmission, ordre garanti | aucune garantie |
| Coût | plus lent | plus léger |
| Usages | HTTP, SSH, bases de données | DNS, visioconférence, jeux |

TCP ouvre la connexion par une **poignée de main en trois temps** : `SYN` → `SYN-ACK` → `ACK`. UDP envoie sans prévenir : si un paquet se perd, tant pis. Pour un appel vidéo, mieux vaut une image sautée qu'une image en retard.'''},
                {"type": "text", "md": '''Personne ne retient des adresses IP. Le **DNS** traduit un nom (`revisionna.fr`) en adresse. La résolution remonte une hiérarchie : serveurs racine, puis ceux du domaine de premier niveau (`.fr`), puis le serveur qui fait **autorité** sur le domaine. Chaque réponse est mise en cache pour la durée de son **TTL**.

| Enregistrement | Rôle |
|---|---|
| `A` | nom → adresse IPv4 |
| `AAAA` | nom → adresse IPv6 |
| `CNAME` | alias vers un autre nom |
| `MX` | serveur de messagerie du domaine |
| `TXT` | texte libre (vérifications, SPF) |'''},
                {"type": "code", "lang": "bash", "code": '''dig revisionna.fr A +short       # l'adresse derrière le nom
dig revisionna.fr MX             # les serveurs de messagerie
cat /etc/resolv.conf             # le résolveur qu'utilise la machine
cat /etc/hosts                   # les correspondances locales, lues avant le DNS'''},
                {"type": "callout", "tone": "warn", "md": "Une modification DNS n'est pas instantanée : les anciens enregistrements restent en cache jusqu'à l'expiration de leur TTL. Avant une migration, on **baisse le TTL** quelques jours à l'avance."},
                {"type": "text", "md": '''**DHCP** distribue automatiquement la configuration réseau à une machine qui se connecte : son adresse IP, le masque, la **passerelle par défaut** et les serveurs DNS. L'échange tient en quatre messages (*Discover, Offer, Request, Acknowledge*), et l'adresse est prêtée pour une durée limitée : le **bail**.

Les serveurs, eux, reçoivent en général une adresse **fixe** : on ne veut pas que l'adresse de la base de données change pendant la nuit.'''},
                {"type": "quiz", "id": "q1", "question": "Sur quel port écoute HTTPS par défaut ?", "choices": ["22", "80", "443", "8080"], "answer": "443", "explanation": "80 pour HTTP, 443 pour HTTPS, 22 pour SSH."},
                {"type": "quiz", "id": "q2", "question": "Quel protocole garantit l'arrivée et l'ordre des données ?", "choices": ["UDP", "TCP", "IP", "ICMP"], "answer": "TCP", "explanation": "TCP accuse réception et retransmet ; UDP n'offre aucune garantie."},
                {"type": "quiz", "id": "q3", "question": "Quel enregistrement DNS associe un nom à une adresse IPv4 ?", "choices": ["MX", "CNAME", "A", "TXT"], "answer": "A", "explanation": "`AAAA` fait la même chose pour IPv6."},
                {"type": "quiz", "id": "q4", "question": "Que fournit un serveur DHCP ?", "choices": ["Des certificats HTTPS", "L'adresse IP, le masque, la passerelle et les DNS", "Des noms de domaine", "Un pare-feu"], "answer": "L'adresse IP, le masque, la passerelle et les DNS", "explanation": "Toute la configuration réseau d'une machine, pour la durée du bail."},
            ],
        },
        {
            "slug": "routage-pare-feu-et-diagnostic",
            "title": "Routage, NAT, pare-feu et diagnostic",
            "duration_min": 25,
            "blocks": [
                {"type": "text", "md": '''Deux machines du **même réseau** se parlent directement. Pour joindre un **autre réseau**, la machine envoie son paquet à sa **passerelle par défaut**, un **routeur**. Celui-ci consulte sa **table de routage**, choisit le prochain saut, et ainsi de suite jusqu'à la destination.

Le **commutateur** (*switch*) relie les machines d'un même réseau local et travaille avec les adresses MAC ; le **routeur** relie des réseaux entre eux et travaille avec les adresses IP.'''},
                {"type": "code", "lang": "bash", "code": '''ip addr                  # les interfaces et leurs adresses
ip route                 # la table de routage
# default via 192.168.1.1 dev eth0      <- la passerelle par défaut
# 192.168.1.0/24 dev eth0               <- le réseau local, joint directement'''},
                {"type": "text", "md": '''Les adresses privées ne circulent pas sur Internet. Le **NAT** (*traduction d'adresses*) règle le problème : la box ou le routeur remplace l'adresse privée de l'émetteur par sa propre adresse publique, et note la correspondance pour acheminer la réponse. Tout un réseau local partage ainsi une seule adresse publique.

Dans l'autre sens, pour exposer un service interne, on configure une **redirection de port** : « ce qui arrive sur le port 443 de l'adresse publique part vers `192.168.1.10:443` ».'''},
                {"type": "text", "md": '''Un **pare-feu** filtre le trafic selon des règles : adresse source, port de destination, protocole. La bonne politique est **tout refuser par défaut**, puis n'ouvrir que le nécessaire. Les règles se lisent dans l'ordre : **la première qui correspond s'applique**.'''},
                {"type": "code", "lang": "bash", "code": '''# ufw, le pare-feu simplifié d'Ubuntu
sudo ufw default deny incoming     # tout refuser en entrée
sudo ufw default allow outgoing    # tout autoriser en sortie
sudo ufw allow 22/tcp              # SSH (à faire AVANT d'activer !)
sudo ufw allow 80,443/tcp          # le site web
sudo ufw enable
sudo ufw status verbose'''},
                {"type": "callout", "tone": "warn", "md": "N'exposez jamais une base de données sur Internet. PostgreSQL ou MongoDB n'écoutent que sur le réseau interne ; seul le serveur web est joignable de l'extérieur. C'est ce que fait le fichier Compose de cette application : la base n'a aucun port publié."},
                {"type": "text", "md": '''**SSH** ouvre un shell chiffré sur une machine distante. On s'authentifie de préférence par **paire de clés** : la clé privée reste sur votre poste, la clé publique est déposée sur le serveur. Trois réglages de base dans `/etc/ssh/sshd_config` : interdire la connexion directe de root, interdire les mots de passe, n'autoriser que les clés.'''},
                {"type": "code", "lang": "bash", "code": '''ssh-keygen -t ed25519                  # créer une paire de clés
ssh-copy-id alice@serveur.example      # déposer la clé publique
ssh alice@serveur.example              # se connecter
scp sauvegarde.sql.gz alice@serveur.example:/srv/   # copier un fichier'''},
                {"type": "text", "md": '''Quand « ça ne marche pas », on remonte les couches une à une, du bas vers le haut :

| Question | Commande |
|---|---|
| Ai-je une adresse ? | `ip addr` |
| La machine répond-elle ? | `ping 192.168.1.1` |
| Par où passent mes paquets ? | `traceroute example.com` |
| Le nom se résout-il ? | `dig example.com` |
| Le port est-il ouvert ? | `nc -zv example.com 443` |
| Qui écoute chez moi ? | `ss -tlnp` |
| Le service répond-il ? | `curl -I https://example.com` |

Si `ping 8.8.8.8` fonctionne mais pas `ping example.com`, le réseau va bien : c'est le **DNS** qui est en cause.'''},
                {"type": "quiz", "id": "q1", "question": "À qui une machine envoie-t-elle un paquet destiné à un autre réseau ?", "choices": ["Au serveur DNS", "À sa passerelle par défaut", "Au serveur DHCP", "À toutes les machines du réseau"], "answer": "À sa passerelle par défaut", "explanation": "Le routeur se charge de l'acheminer vers le prochain saut."},
                {"type": "quiz", "id": "q2", "question": "Quelle politique de pare-feu adopter par défaut ?", "choices": ["Tout autoriser, puis bloquer ce qui gêne", "Tout refuser en entrée, puis ouvrir le nécessaire", "Aucune règle", "Bloquer uniquement le port 22"], "answer": "Tout refuser en entrée, puis ouvrir le nécessaire", "explanation": "On ne peut pas lister tout ce qui est dangereux ; on peut lister ce qui est utile."},
                {"type": "quiz", "id": "q3", "question": "`ping 8.8.8.8` répond, `ping example.com` échoue. Où est le problème ?", "choices": ["Le câble", "La passerelle", "La résolution DNS", "Le pare-feu du serveur"], "answer": "La résolution DNS", "explanation": "La connectivité IP fonctionne : c'est la traduction du nom qui échoue."},
                {"type": "quiz", "id": "q4", "question": "Dans une paire de clés SSH, que dépose-t-on sur le serveur ?", "choices": ["La clé privée", "La clé publique", "Les deux", "Le mot de passe"], "answer": "La clé publique", "explanation": "La clé privée ne quitte jamais votre poste."},
                {"type": "quiz", "id": "q5", "question": "À quoi sert le NAT ?", "choices": ["À chiffrer le trafic", "À faire sortir des adresses privées derrière une adresse publique", "À traduire les noms en adresses", "À distribuer les adresses IP"], "answer": "À faire sortir des adresses privées derrière une adresse publique", "explanation": "Le DNS traduit les noms ; le DHCP distribue les adresses."},
            ],
        },
    ],
    "exercises": [
        {
            "slug": "tp-sous-reseau",
            "title": "Calculer un sous-réseau",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Écrivez `sous_reseau(cidr)`, qui reçoit une adresse en notation CIDR et renvoie un dictionnaire :

```python
sous_reseau("192.168.1.130/26")
# {"reseau": "192.168.1.128", "diffusion": "192.168.1.191", "masque": "255.255.255.192", "hotes": 62}
```

- `"reseau"` : l'adresse du réseau (bits d'hôte à 0) ;
- `"diffusion"` : l'adresse de diffusion (bits d'hôte à 1) ;
- `"masque"` : le masque en notation décimale pointée ;
- `"hotes"` : le nombre d'hôtes utilisables, soit `2^(32-n) - 2` (et 0 pour un /31 ou un /32).

Faites le calcul vous-même, sans le module `ipaddress` : convertissez l'adresse en un entier de 32 bits, puis utilisez les opérateurs `&`, `|` et les décalages.''',
            "starter_code": '''def sous_reseau(cidr):
    ...
''',
            "solution": '''def sous_reseau(cidr):
    adresse, prefixe = cidr.split("/")
    prefixe = int(prefixe)

    entier = 0
    for octet in adresse.split("."):
        entier = (entier << 8) | int(octet)

    tout = 0xFFFFFFFF
    masque = (tout << (32 - prefixe)) & tout
    reseau = entier & masque
    diffusion = reseau | (tout ^ masque)

    def en_texte(valeur):
        return ".".join(str((valeur >> decalage) & 255) for decalage in (24, 16, 8, 0))

    return {
        "reseau": en_texte(reseau),
        "diffusion": en_texte(diffusion),
        "masque": en_texte(masque),
        "hotes": max(2 ** (32 - prefixe) - 2, 0),
    }
''',
            "hints": [
                "Convertissez les quatre octets en un seul entier : `entier = (entier << 8) | octet`.",
                "Le masque est une suite de `n` bits à 1 suivie de zéros : `(0xFFFFFFFF << (32 - n)) & 0xFFFFFFFF`.",
                "Réseau = adresse `&` masque. Diffusion = réseau `|` l'inverse du masque.",
            ],
            "spec": {"tests": [
                {"name": "slash_24", "code": "r = sous_reseau('192.168.1.42/24')\nassert r == {'reseau': '192.168.1.0', 'diffusion': '192.168.1.255', 'masque': '255.255.255.0', 'hotes': 254}"},
                {"name": "slash_26", "code": "r = sous_reseau('192.168.1.130/26')\nassert r['reseau'] == '192.168.1.128' and r['diffusion'] == '192.168.1.191' and r['hotes'] == 62"},
                {"name": "masque", "code": "assert sous_reseau('10.1.2.3/26')['masque'] == '255.255.255.192'\nassert sous_reseau('10.1.2.3/12')['masque'] == '255.240.0.0'"},
                {"name": "slash_16", "code": "r = sous_reseau('172.16.5.9/16')\nassert r['reseau'] == '172.16.0.0' and r['diffusion'] == '172.16.255.255' and r['hotes'] == 65534"},
                {"name": "slash_30", "code": "r = sous_reseau('10.0.0.5/30')\nassert r['reseau'] == '10.0.0.4' and r['diffusion'] == '10.0.0.7' and r['hotes'] == 2"},
                {"name": "slash_32", "code": "r = sous_reseau('10.0.0.5/32')\nassert r['reseau'] == '10.0.0.5' and r['hotes'] == 0"},
            ]},
        },
        {
            "slug": "tp-pare-feu",
            "title": "Évaluer des règles de pare-feu",
            "kind": "python",
            "difficulty": "moyen",
            "statement": '''Un pare-feu lit ses règles dans l'ordre : **la première qui correspond décide**. Si aucune ne correspond, la politique par défaut s'applique.

Une règle est un dictionnaire :

```python
{"action": "ACCEPT", "protocole": "tcp", "port": 443, "source": "*"}
```

- `protocole` : `"tcp"`, `"udp"`, ou `"*"` pour n'importe lequel ;
- `port` : un entier, ou `"*"` ;
- `source` : une adresse exacte, un préfixe terminé par un point (`"10.0."` correspond à `10.0.3.7`), ou `"*"`.

Un paquet est un dictionnaire `{"protocole": "tcp", "port": 443, "source": "203.0.113.9"}`.

Écrivez `decider(regles, paquet, defaut="DROP")`, qui renvoie l'action à appliquer.''',
            "starter_code": '''def decider(regles, paquet, defaut="DROP"):
    ...
''',
            "solution": '''def decider(regles, paquet, defaut="DROP"):
    def correspond(regle):
        if regle["protocole"] not in ("*", paquet["protocole"]):
            return False
        if regle["port"] not in ("*", paquet["port"]):
            return False
        source = regle["source"]
        if source == "*":
            return True
        if source.endswith("."):
            return paquet["source"].startswith(source)
        return paquet["source"] == source

    for regle in regles:
        if correspond(regle):
            return regle["action"]
    return defaut
''',
            "hints": [
                "Écrivez d'abord une fonction qui dit si UNE règle correspond au paquet.",
                "Les trois critères doivent correspondre en même temps ; `\"*\"` correspond à tout.",
                "Parcourez les règles dans l'ordre et renvoyez dès la première correspondance.",
            ],
            "spec": {"tests": [
                {"name": "regle_simple", "code": "r = [{'action': 'ACCEPT', 'protocole': 'tcp', 'port': 443, 'source': '*'}]\nassert decider(r, {'protocole': 'tcp', 'port': 443, 'source': '203.0.113.9'}) == 'ACCEPT'"},
                {"name": "politique_par_defaut", "code": "r = [{'action': 'ACCEPT', 'protocole': 'tcp', 'port': 443, 'source': '*'}]\nassert decider(r, {'protocole': 'tcp', 'port': 5432, 'source': '203.0.113.9'}) == 'DROP'\nassert decider([], {'protocole': 'udp', 'port': 53, 'source': '1.1.1.1'}, defaut='ACCEPT') == 'ACCEPT'"},
                {"name": "premiere_regle_gagne", "code": "r = [{'action': 'DROP', 'protocole': '*', 'port': '*', 'source': '198.51.100.7'}, {'action': 'ACCEPT', 'protocole': 'tcp', 'port': 22, 'source': '*'}]\np = {'protocole': 'tcp', 'port': 22, 'source': '198.51.100.7'}\nassert decider(r, p) == 'DROP'\nassert decider(list(reversed(r)), p) == 'ACCEPT'"},
                {"name": "prefixe_de_source", "code": "r = [{'action': 'ACCEPT', 'protocole': 'tcp', 'port': 5432, 'source': '10.0.'}]\nassert decider(r, {'protocole': 'tcp', 'port': 5432, 'source': '10.0.3.7'}) == 'ACCEPT'\nassert decider(r, {'protocole': 'tcp', 'port': 5432, 'source': '10.1.3.7'}) == 'DROP'"},
                {"name": "protocole_distinct", "code": "r = [{'action': 'ACCEPT', 'protocole': 'udp', 'port': 53, 'source': '*'}]\nassert decider(r, {'protocole': 'tcp', 'port': 53, 'source': '10.0.0.1'}) == 'DROP'"},
            ]},
        },
        {
            "slug": "quiz-reseaux",
            "title": "Le réseau en dix questions",
            "kind": "quiz",
            "difficulty": "facile",
            "statement": "Adressage, protocoles et diagnostic : les bases à maîtriser.",
            "spec": {"questions": [
                {"id": "1", "question": "Quel masque correspond à /16 ?", "choices": ["255.0.0.0", "255.255.0.0", "255.255.255.0", "255.255.255.255"], "answer": "255.255.0.0", "explanation": "16 bits à 1 : les deux premiers octets."},
                {"id": "2", "question": "Quel équipement relie deux réseaux différents ?", "choices": ["Un commutateur (switch)", "Un routeur", "Un câble croisé", "Un répéteur Wi-Fi"], "answer": "Un routeur", "explanation": "Le commutateur relie les machines d'un même réseau ; le routeur relie les réseaux."},
                {"id": "3", "question": "Sur quel port écoute SSH par défaut ?", "choices": ["21", "22", "23", "25"], "answer": "22", "explanation": "21 est FTP, 23 Telnet, 25 SMTP."},
                {"id": "4", "question": "Quelle commande montre les ports en écoute sur la machine ?", "choices": ["ss -tlnp", "ping", "dig", "ip route"], "answer": "ss -tlnp", "explanation": "TCP (`t`), en écoute (`l`), numérique (`n`), avec le processus (`p`)."},
                {"id": "5", "question": "Que désigne 127.0.0.1 ?", "choices": ["La passerelle", "La machine elle-même", "Le serveur DNS", "L'adresse de diffusion"], "answer": "La machine elle-même", "explanation": "C'est l'adresse de bouclage, *localhost*."},
                {"id": "6", "question": "Quel protocole pour un appel vidéo en direct ?", "choices": ["TCP, pour ne rien perdre", "UDP, pour ne pas attendre les paquets perdus", "ICMP", "DHCP"], "answer": "UDP, pour ne pas attendre les paquets perdus", "explanation": "Une image en retard ne sert plus à rien : mieux vaut la sauter."},
                {"id": "7", "question": "Combien d'hôtes utilisables dans un /30 ?", "choices": ["2", "4", "30", "6"], "answer": "2", "explanation": "2^2 = 4 adresses, moins le réseau et la diffusion."},
                {"id": "8", "question": "Vous changez l'adresse IP d'un site. Pourquoi certains visiteurs arrivent-ils encore sur l'ancienne ?", "choices": ["Leur navigateur est trop ancien", "L'ancien enregistrement DNS est en cache jusqu'à l'expiration du TTL", "Le pare-feu les bloque", "Le DHCP n'a pas renouvelé leur bail"], "answer": "L'ancien enregistrement DNS est en cache jusqu'à l'expiration du TTL", "explanation": "D'où l'intérêt de baisser le TTL avant une migration."},
                {"id": "9", "question": "Quelle commande montre le chemin suivi par les paquets ?", "choices": ["traceroute", "curl", "whoami", "df"], "answer": "traceroute", "explanation": "Elle liste les routeurs traversés jusqu'à la destination."},
                {"id": "10", "question": "Faut-il publier le port de PostgreSQL sur Internet ?", "choices": ["Oui, pour le déboguer plus facilement", "Non : seul le réseau interne doit y accéder", "Oui, si le mot de passe est long", "Seulement en UDP"], "answer": "Non : seul le réseau interne doit y accéder", "explanation": "On réduit la surface d'attaque : seul le serveur web est exposé."},
            ]},
        },
    ],
}
