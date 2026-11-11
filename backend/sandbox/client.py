"""Client du service de correction : HTTP sur socket Unix, bibliothèque standard."""
from __future__ import annotations

import http.client
import json
import socket


class RunnerUnavailable(RuntimeError):
    """Le service de correction ne répond pas."""


class _UnixConnection(http.client.HTTPConnection):
    def __init__(self, path: str, timeout: float):
        super().__init__("runner", timeout=timeout)
        self._path = path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self._path)


def _request(socket_path: str, method: str, path: str, body: dict | None, timeout: float) -> dict:
    connection = _UnixConnection(socket_path, timeout)
    try:
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"} if data else {}
        connection.request(method, path, body=data, headers=headers)
        response = connection.getresponse()
        payload = json.loads(response.read() or b"{}")
    except (OSError, ValueError, http.client.HTTPException) as exc:
        raise RunnerUnavailable(str(exc)) from exc
    finally:
        connection.close()
    if response.status != 200:
        raise RunnerUnavailable(payload.get("error") or f"statut {response.status}")
    return payload


def run(socket_path: str, job: dict, *, timeout: float = 40) -> dict:
    return _request(socket_path, "POST", "/run", job, timeout)


def health(socket_path: str, *, timeout: float = 3) -> dict:
    return _request(socket_path, "GET", "/health", None, timeout)
