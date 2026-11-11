"""Service de correction isolé : serveur HTTP minimal sur un socket Unix.

Il tourne dans son propre conteneur, sans réseau (`network_mode: none`), sans
secret, sur un système de fichiers en lecture seule. L'API lui parle par un
socket Unix placé sur un volume partagé.

Lancé en root, il exécute chaque travail sous un compte Unix jetable différent
(un par « créneau ») : le code d'un élève ne peut ni tuer le serveur, ni lire
sa mémoire, ni gêner le travail d'un autre élève.

    python -m sandbox.server
"""
from __future__ import annotations

import json
import logging
import os
import queue
import socketserver
from http.server import BaseHTTPRequestHandler

from . import core

log = logging.getLogger("sandbox")

MAX_BODY = 512 * 1024
SLOT_WAIT_SECONDS = 15


class Settings:
    def __init__(self, env=os.environ):
        self.socket_path = env.get("RUNNER_SOCKET", "/run/sandbox/runner.sock")
        self.socket_gid = int(env["SOCKET_GID"]) if env.get("SOCKET_GID") else None
        self.slots = max(1, int(env.get("SANDBOX_SLOTS", "3")))
        self.uid_base = int(env.get("SANDBOX_UID_BASE", "20000"))
        self.tmp = env.get("SANDBOX_TMP") or None
        self.timeout = int(env.get("SANDBOX_TIMEOUT", str(core.DEFAULT_TIMEOUT)))


class RunnerServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, settings: Settings):
        self.settings = settings
        self.isolated = os.geteuid() == 0
        # Un créneau = un compte jetable. Sans root, pas de changement de compte.
        self.slots: queue.Queue = queue.Queue()
        for index in range(settings.slots):
            uid = settings.uid_base + index
            self.slots.put((uid, uid) if self.isolated else None)

        if settings.tmp:
            os.makedirs(settings.tmp, mode=0o711, exist_ok=True)
        if os.path.exists(settings.socket_path):
            os.unlink(settings.socket_path)
        super().__init__(settings.socket_path, Handler)
        os.chmod(settings.socket_path, 0o660)
        if self.isolated and settings.socket_gid is not None:
            os.chown(settings.socket_path, 0, settings.socket_gid)

    def run_job(self, job: dict) -> dict:
        try:
            identity = self.slots.get(timeout=SLOT_WAIT_SECONDS)
        except queue.Empty:
            return {"passed": False, "score": 0.0, "results": [],
                    "output": "Le correcteur est très sollicité, réessayez dans un instant."}
        try:
            options = {"timeout": self.settings.timeout, "identity": identity,
                       "base_dir": self.settings.tmp}
            if job.get("kind") == "sql":
                return core.run_sql(str(job.get("query", "")), job.get("spec") or {}, **options)
            return core.run_python(str(job.get("code", "")), job.get("tests") or [], **options)
        finally:
            self.slots.put(identity)


class Handler(BaseHTTPRequestHandler):
    server: RunnerServer
    timeout = 10

    def address_string(self):  # socket Unix : pas d'adresse cliente
        return "api"

    def log_message(self, fmt, *args):
        log.info(fmt, *args)

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 - nom imposé par http.server
        if self.path == "/health":
            self._send(200, {"status": "ok", "isolated": self.server.isolated})
        else:
            self._send(404, {"error": "introuvable"})

    def do_POST(self):  # noqa: N802
        if self.path != "/run":
            return self._send(404, {"error": "introuvable"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if not 0 < length <= MAX_BODY:
            return self._send(413, {"error": "corps de requête invalide"})
        try:
            job = json.loads(self.rfile.read(length))
        except ValueError:
            return self._send(400, {"error": "JSON invalide"})
        if not isinstance(job, dict) or job.get("kind") not in ("python", "sql"):
            return self._send(400, {"error": "type de travail inconnu"})

        try:
            result = self.server.run_job(job)
        except Exception:  # noqa: BLE001 - le service doit rester debout
            log.exception("échec d'un travail")
            return self._send(500, {"error": "erreur interne du correcteur"})
        self._send(200, result)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    settings = Settings()
    server = RunnerServer(settings)
    log.info(
        "correcteur prêt sur %s (%d créneaux, comptes jetables : %s)",
        settings.socket_path, settings.slots, "oui" if server.isolated else "NON, pas root",
    )
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
