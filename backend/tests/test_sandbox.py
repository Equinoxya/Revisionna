"""Le bac à sable : limites de ressources, cloisonnement, service isolé."""
import os
import tempfile
import threading

import pytest

from sandbox import client, core
from sandbox.server import RunnerServer, Settings

DOUBLE = [{"name": "double", "code": "assert double(2) == 4"},
          {"name": "zero", "code": "assert double(0) == 0"}]

SCHEMA = """
CREATE TABLE notes (eleve TEXT, note REAL);
INSERT INTO notes VALUES ('Alice', 16), ('Bob', 9), ('Chloé', 12.5);
"""
SPEC = {"schema": SCHEMA, "expected_query": "SELECT eleve FROM notes WHERE note >= 10"}


def test_python_reussi():
    result = core.run_python("def double(n):\n    return n * 2\n", DOUBLE)
    assert result["passed"] is True
    assert result["score"] == 1.0
    assert [item["passed"] for item in result["results"]] == [True, True]


def test_python_echec_partiel():
    result = core.run_python("def double(n):\n    return 4\n", DOUBLE)
    assert result["passed"] is False
    assert result["score"] == 0.5


def test_erreur_de_syntaxe_expliquee():
    result = core.run_python("def double(n)\n    return n * 2\n", DOUBLE)
    assert result["passed"] is False
    assert "SyntaxError" in result["output"]
    assert "harness.py" not in result["output"]  # on ne montre que le code de l'élève


def test_boucle_infinie_interrompue():
    result = core.run_python("while True:\n    pass\n", DOUBLE, timeout=8)
    assert result["passed"] is False
    assert "interrompue" in result["output"] or "Temps dépassé" in result["output"]


def test_sortie_geante_interrompue():
    code = "import sys\nwhile True:\n    sys.__stdout__.write('x' * 100000)\n"
    result = core.run_python(code, DOUBLE)
    assert result["passed"] is False
    assert "interrompue" in result["output"]


def test_bombe_memoire_contenue():
    result = core.run_python("x = bytearray(10 ** 10)\n", DOUBLE)
    assert result["passed"] is False
    assert "MemoryError" in result["output"]


def test_environnement_du_serveur_invisible(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "ne-doit-pas-fuiter")
    code = "import os\nprint(sorted(os.environ))\ndef double(n):\n    return n * 2\n"
    result = core.run_python(code, DOUBLE)
    assert result["passed"] is True
    assert "JWT_SECRET_KEY" not in result["stdout"]
    assert "ne-doit-pas-fuiter" not in result["output"]


def test_resultat_forge_ne_valide_pas_les_tests():
    # L'élève imprime lui-même une « dernière ligne » vide de résultats.
    code = (
        "import atexit, json, sys\n"
        "atexit.register(lambda: sys.__stdout__.write("
        "'\\n' + json.dumps({'results': [], 'stdout': '', 'error': None}) + '\\n'))\n"
    )
    result = core.run_python(code, DOUBLE)
    assert result["passed"] is False
    assert len(result["results"]) == len(DOUBLE)


def test_sql_correct_sans_tenir_compte_de_l_ordre():
    result = core.run_sql("SELECT eleve FROM notes WHERE note >= 10 ORDER BY eleve DESC", SPEC)
    assert result["passed"] is True
    assert result["columns"] == ["eleve"]
    assert sorted(row[0] for row in result["rows"]) == ["Alice", "Chloé"]


def test_sql_incorrect_montre_l_attendu():
    result = core.run_sql("SELECT eleve FROM notes", SPEC)
    assert result["passed"] is False
    assert len(result["expected_rows"]) == 2


def test_sql_invalide():
    result = core.run_sql("SELECT * FROM table_absente", SPEC)
    assert result["passed"] is False
    assert result["output"].startswith("Erreur SQL")


@pytest.mark.parametrize("query", [
    "ATTACH DATABASE '/tmp/vol.db' AS vol",
    "PRAGMA database_list",
    "SELECT 1; SELECT 2",
])
def test_sql_hors_perimetre_refuse(query):
    result = core.run_sql(query, SPEC)
    assert result["passed"] is False
    assert result["output"].startswith("Erreur SQL")


def test_sql_interminable_interrompu():
    query = "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT count(*) FROM c"
    result = core.run_sql(query, SPEC, timeout=8)
    assert result["passed"] is False
    assert "interrompue" in result["output"] or "Temps dépassé" in result["output"]


def test_comparaison_sql_tolere_les_arrondis():
    assert core.same_rows([["a", 0.1 + 0.2]], [["a", 0.3]], ordered=True)
    assert not core.same_rows([["a", 1]], [["a", 2]], ordered=True)
    assert not core.same_rows([["a"], ["b"]], [["b"], ["a"]], ordered=True)
    assert core.same_rows([["a"], ["b"]], [["b"], ["a"]], ordered=False)


@pytest.fixture()
def service():
    """Le service isolé, démarré sur un socket temporaire."""
    workdir = tempfile.mkdtemp(prefix="runner-", dir="/tmp")
    os.chmod(workdir, 0o711)  # traversable par les comptes jetables
    settings = Settings(env={
        "RUNNER_SOCKET": os.path.join(workdir, "runner.sock"),
        "SANDBOX_TMP": os.path.join(workdir, "jobs"),
        "SANDBOX_SLOTS": "2",
    })
    server = RunnerServer(settings)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def test_service_aller_retour(service):
    path = service.settings.socket_path
    assert client.health(path)["status"] == "ok"

    python = client.run(path, {"kind": "python", "code": "def double(n):\n    return n * 2\n",
                               "tests": DOUBLE})
    assert python["passed"] is True

    sql = client.run(path, {"kind": "sql", "query": SPEC["expected_query"], "spec": SPEC})
    assert sql["passed"] is True


def test_service_refuse_un_travail_inconnu(service):
    with pytest.raises(client.RunnerUnavailable):
        client.run(service.settings.socket_path, {"kind": "shell", "code": "ls"})


def test_service_absent_signale(tmp_path):
    with pytest.raises(client.RunnerUnavailable):
        client.health(str(tmp_path / "absent.sock"))


@pytest.mark.skipif(os.geteuid() != 0, reason="le changement de compte exige root")
def test_compte_jetable_cloisonne(service):
    """En root (comme dans le conteneur), le code tourne sous un autre compte."""
    code = (
        "import os, pathlib\n"
        "print('UID', os.getuid())\n"
        "try:\n"
        "    pathlib.Path(f'/proc/{os.getppid()}/environ').read_bytes()\n"
        "    print('ENVIRON lisible')\n"
        "except PermissionError:\n"
        "    print('ENVIRON refusé')\n"
        "try:\n"
        "    os.kill(os.getppid(), 0)\n"
        "    print('SIGNAL possible')\n"
        "except PermissionError:\n"
        "    print('SIGNAL refusé')\n"
        "def double(n):\n    return n * 2\n"
    )
    result = client.run(service.settings.socket_path,
                        {"kind": "python", "code": code, "tests": DOUBLE})
    assert service.isolated is True
    assert result["passed"] is True
    uid = int(result["stdout"].split("UID ")[1].split()[0])
    assert uid >= service.settings.uid_base
    assert "ENVIRON refusé" in result["stdout"]
    assert "SIGNAL refusé" in result["stdout"]
