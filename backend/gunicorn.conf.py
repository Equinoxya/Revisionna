"""Réglages de gunicorn (serveur d'application de production)."""
import os

bind = "0.0.0.0:5000"
# Plusieurs processus, plusieurs fils par processus : une correction de TP
# occupe un fil pendant quelques secondes sans bloquer les autres requêtes.
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
threads = int(os.getenv("WEB_THREADS", "4"))
worker_class = "gthread"
timeout = 60
# Le système de fichiers du conteneur est en lecture seule : les fichiers de
# battement des workers vont en mémoire.
worker_tmp_dir = "/dev/shm"
accesslog = "-"
errorlog = "-"
