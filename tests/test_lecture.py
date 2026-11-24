from fastapi.testclient import TestClient

from app.interpreter.interpreter import (
    MAX_ENTREES,
    MAX_LONGUEUR_ENTREE,
    executer_code,
)
from app.main import app

client = TestClient(app)


def test_lire_un_entier():
    r = executer_code("DEBUT LIRE(x) ECRIRE(x * 2) FIN", ["21"])
    assert r == {"output": "42", "error": None}


def test_lire_un_reel():
    r = executer_code("DEBUT LIRE(x) ECRIRE(x + 1) FIN", ["2.5"])
    assert r == {"output": "3.5", "error": None}


def test_lire_un_nombre_negatif():
    r = executer_code("DEBUT LIRE(x) ECRIRE(x + 1) FIN", ["-5"])
    assert r == {"output": "-4", "error": None}


def test_lire_un_nombre_avec_espaces():
    r = executer_code("DEBUT LIRE(x) ECRIRE(x + 1) FIN", ["  7  "])
    assert r == {"output": "8", "error": None}


def test_lire_un_texte():
    r = executer_code("DEBUT LIRE(nom) ECRIRE(nom) FIN", ["Awa"])
    assert r == {"output": "Awa", "error": None}


def test_lire_un_texte_garde_ses_espaces():
    r = executer_code("DEBUT LIRE(t) ECRIRE(t + \"!\") FIN", ["  salut "])
    assert r == {"output": "  salut !", "error": None}


def test_lire_nan_et_inf_restent_des_textes():
    for mot in ["nan", "inf", "-inf", "1e5"]:
        r = executer_code("DEBUT LIRE(x) ECRIRE(x) FIN", [mot])
        assert r == {"output": mot, "error": None}


def test_deux_lire_consomment_les_saisies_dans_l_ordre():
    r = executer_code("DEBUT LIRE(a) LIRE(b) ECRIRE(a - b) FIN", ["10", "3"])
    assert r == {"output": "7", "error": None}


def test_lire_dans_une_boucle_pour():
    code = "DEBUT POUR i DE 1 A 3 FAIRE LIRE(x) ECRIRE(x) FINPOUR FIN"
    r = executer_code(code, ["a", "b", "c"])
    assert r == {"output": "a\nb\nc", "error": None}


def test_lire_dans_un_si():
    code = """DEBUT
      LIRE(age)
      SI age >= 18 ALORS
        ECRIRE("majeur")
      SINON
        ECRIRE("mineur")
      FINSI
    FIN"""
    assert executer_code(code, ["20"])["output"] == "majeur"
    assert executer_code(code, ["15"])["output"] == "mineur"


def test_lire_dans_un_tant_que():
    code = """DEBUT
      LIRE(n)
      TANT QUE n > 0 FAIRE
        ECRIRE(n)
        LIRE(n)
      FINTANTQUE
    FIN"""
    r = executer_code(code, ["3", "2", "0"])
    assert r == {"output": "3\n2", "error": None}


def test_lire_ecrase_une_variable_existante():
    r = executer_code("DEBUT x <- 1 LIRE(x) ECRIRE(x) FIN", ["9"])
    assert r == {"output": "9", "error": None}


def test_saisie_manquante():
    r = executer_code("DEBUT LIRE(x) LIRE(y) FIN", ["1"])
    assert r["output"] == ""
    assert "Saisie manquante" in r["error"]
    assert "n°2" in r["error"]


def test_lire_sans_inputs():
    r = executer_code("DEBUT LIRE(x) FIN")
    assert r["output"] == ""
    assert "Saisie manquante" in r["error"]


def test_saisies_en_trop_ignorees():
    r = executer_code("DEBUT LIRE(x) ECRIRE(x) FIN", ["1", "2", "3"])
    assert r == {"output": "1", "error": None}


def test_calcul_sur_un_texte_lu():
    r = executer_code("DEBUT LIRE(x) ECRIRE(x * 2) FIN", ["abc"])
    assert "Opération impossible" in r["error"]


def test_lire_dans_un_mot_reserve():
    r = executer_code("DEBUT LIRE(ECRIRE) FIN", ["1"])
    assert r["output"] == ""
    assert r["error"] is not None


def test_lire_sans_parentheses_est_une_erreur_de_syntaxe():
    r = executer_code("DEBUT LIRE x FIN", ["1"])
    assert "syntaxe" in r["error"].lower()


def test_trop_de_saisies():
    r = executer_code("DEBUT ECRIRE(1) FIN", ["x"] * (MAX_ENTREES + 1))
    assert "Trop de saisies" in r["error"]


def test_saisie_trop_longue():
    r = executer_code("DEBUT ECRIRE(1) FIN", ["a" * (MAX_LONGUEUR_ENTREE + 1)])
    assert "dépasse" in r["error"]


def test_nombre_limite_de_saisies_accepte():
    r = executer_code("DEBUT ECRIRE(1) FIN", ["x"] * MAX_ENTREES)
    assert r == {"output": "1", "error": None}


def test_route_run_avec_inputs():
    reponse = client.post(
        "/run", json={"code": "DEBUT LIRE(x) ECRIRE(x * 2) FIN", "inputs": ["21"]}
    )
    assert reponse.status_code == 200
    assert reponse.json() == {"output": "42", "error": None}


def test_route_run_sans_inputs_reste_compatible():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(1 + 2) FIN"})
    assert reponse.status_code == 200
    assert reponse.json() == {"output": "3", "error": None}


def test_route_run_refuse_des_saisies_qui_ne_sont_pas_des_textes():
    reponse = client.post(
        "/run", json={"code": "DEBUT LIRE(x) ECRIRE(x) FIN", "inputs": [21]}
    )
    assert reponse.status_code == 422