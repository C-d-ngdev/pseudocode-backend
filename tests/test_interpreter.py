from fastapi.testclient import TestClient

from app.interpreter.interpreter import executer_code
from app.main import app

client = TestClient(app)


def test_affichage_texte_et_nombre():
    r = executer_code('DEBUT ECRIRE("Bonjour") ECRIRE(5) FIN')
    assert r == {"output": "Bonjour\n5", "error": None}


def test_affectation_et_variable():
    r = executer_code("DEBUT x <- 5 y = x ECRIRE(y) FIN")
    assert r == {"output": "5", "error": None}


def test_calcul_division_donne_un_reel():
    assert executer_code("DEBUT ECRIRE(7 / 2) FIN")["output"] == "3.5"
    assert executer_code("DEBUT ECRIRE(10 / 2) FIN")["output"] == "5.0"


def test_priorite_des_operateurs():
    assert executer_code("DEBUT ECRIRE(2 + 3 * 4) FIN")["output"] == "14"
    assert executer_code("DEBUT ECRIRE((2 + 3) * 4) FIN")["output"] == "20"
    assert executer_code("DEBUT ECRIRE(5 - 2 + 1) FIN")["output"] == "4"


def test_exemple_de_la_tache():
    code = """DEBUT
  x <- 5
  y <- x * 2 + 1
  ECRIRE("Résultat : ")
  ECRIRE(y)
FIN"""
    r = executer_code(code)
    assert r == {"output": "Résultat : \n11", "error": None}


def test_erreur_variable_non_declaree():
    r = executer_code("DEBUT ECRIRE(z) FIN")
    assert r["output"] == ""
    assert r["error"] is not None
    assert "z" in r["error"]


def test_erreur_division_par_zero():
    r = executer_code("DEBUT ECRIRE(1 / 0) FIN")
    assert r["output"] == ""
    assert r["error"] is not None


def test_erreur_de_syntaxe():
    r = executer_code("DEBUT ECRIRE( FIN")
    assert r["output"] == ""
    assert r["error"] is not None


def test_route_run_succes():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(1 + 2) FIN"})
    assert reponse.status_code == 200
    assert reponse.json() == {"output": "3", "error": None}


def test_route_run_erreur_reste_en_200():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(z) FIN"})
    assert reponse.status_code == 200
    assert reponse.json()["error"] is not None