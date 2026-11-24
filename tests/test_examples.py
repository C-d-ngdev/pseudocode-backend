import pytest
from fastapi.testclient import TestClient

from app.interpreter.exemples import EXEMPLES
from app.interpreter.interpreter import executer_code
from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("exemple", EXEMPLES, ids=[e["cle"] for e in EXEMPLES])
def test_exemple_donne_le_resultat_annonce(exemple):
    resultat = executer_code(exemple["code"], exemple.get("inputs"))
    if exemple["erreur"] is None:
        assert resultat == {"output": exemple["sortie"], "error": None}
    else:
        assert resultat["output"] == ""
        assert exemple["erreur"] in resultat["error"]


def test_cles_des_exemples_uniques():
    cles = [e["cle"] for e in EXEMPLES]
    assert len(cles) == len(set(cles))


def test_page_de_documentation_accessible():
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_exemples_presents_dans_la_documentation():
    schema = client.get("/openapi.json").json()
    corps = schema["paths"]["/run"]["post"]["requestBody"]["content"]["application/json"]
    assert set(corps["examples"]) == {e["cle"] for e in EXEMPLES}


def test_exemple_lecture_affiche_les_saisies_dans_la_documentation():
    schema = client.get("/openapi.json").json()
    corps = schema["paths"]["/run"]["post"]["requestBody"]["content"]["application/json"]
    assert corps["examples"]["lecture"]["value"]["inputs"] == ["Awa", "20"]
    # Un exemple sans saisies n'a pas de champ inputs
    assert "inputs" not in corps["examples"]["affichage"]["value"]


def test_route_run_accepte_chaque_exemple():
    for exemple in EXEMPLES:
        reponse = client.post(
            "/run",
            json={"code": exemple["code"], "inputs": exemple.get("inputs", [])},
        )
        assert reponse.status_code == 200
        corps = reponse.json()
        if exemple["erreur"] is None:
            assert corps == {"output": exemple["sortie"], "error": None}
        else:
            assert exemple["erreur"] in corps["error"]