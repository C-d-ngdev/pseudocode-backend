from fastapi.testclient import TestClient

from app.interpreter.interpreter import executer_code, message_syntaxe
from app.main import app

client = TestClient(app)


def sortie(code):
    return executer_code(code)["output"]


def erreur(code):
    return executer_code(code)["error"]




def test_affichage_texte_et_nombre():
    r = executer_code('DEBUT ECRIRE("Bonjour") ECRIRE(5) FIN')
    assert r == {"output": "Bonjour\n5", "error": None}


def test_affectation_et_variable():
    r = executer_code("DEBUT x <- 5 y = x ECRIRE(y) FIN")
    assert r == {"output": "5", "error": None}


def test_calcul_division_donne_un_reel():
    assert sortie("DEBUT ECRIRE(7 / 2) FIN") == "3.5"
    assert sortie("DEBUT ECRIRE(10 / 2) FIN") == "5.0"


def test_priorite_des_operateurs():
    assert sortie("DEBUT ECRIRE(2 + 3 * 4) FIN") == "14"
    assert sortie("DEBUT ECRIRE((2 + 3) * 4) FIN") == "20"
    assert sortie("DEBUT ECRIRE(5 - 2 + 1) FIN") == "4"


def test_chaines_d_operations_de_gauche_a_droite():
    assert sortie("DEBUT ECRIRE(10 - 3 - 2) FIN") == "5"
    assert sortie("DEBUT ECRIRE(8 / 4 / 2) FIN") == "1.0"


def test_exemple_de_la_tache():
    code = """DEBUT
  x <- 5
  y <- x * 2 + 1
  ECRIRE("Résultat : ")
  ECRIRE(y)
FIN"""
    r = executer_code(code)
    assert r == {"output": "Résultat : \n11", "error": None}


def test_nombres_negatifs():
    assert sortie("DEBUT x = -3 ECRIRE(x) FIN") == "-3"
    assert sortie("DEBUT ECRIRE(5 - -3) FIN") == "8"
    assert sortie("DEBUT ECRIRE(-(2 + 3)) FIN") == "-5"


def test_concatenation_de_textes():
    assert sortie('DEBUT ECRIRE("Bon" + "jour") FIN') == "Bonjour"


def test_affichage_des_reels_arrondi():
    assert sortie("DEBUT ECRIRE(0.1 + 0.2) FIN") == "0.3"


def test_sequences_d_echappement():
    assert sortie('DEBUT ECRIRE("a\\nb") FIN') == "a\nb"
    assert sortie('DEBUT ECRIRE("dit \\"oui\\"") FIN') == 'dit "oui"'


def test_variables_non_conservees_entre_deux_executions():
    assert sortie("DEBUT x = 5 ECRIRE(x) FIN") == "5"
    r = executer_code("DEBUT ECRIRE(x) FIN")
    assert r["output"] == ""
    assert r["error"] == "Variable x non déclarée"




def test_erreur_variable_non_declaree():
    r = executer_code("DEBUT ECRIRE(z) FIN")
    assert r == {"output": "", "error": "Variable z non déclarée"}


def test_erreur_division_par_zero():
    r = executer_code("DEBUT ECRIRE(1 / 0) FIN")
    assert r == {"output": "", "error": "Division par zéro"}


def test_erreur_texte_plus_nombre():
    assert erreur('DEBUT ECRIRE("a" + 1) FIN') == (
        "Opération impossible : « + » entre un texte et un nombre"
    )


def test_erreur_texte_multiplie():
    assert erreur('DEBUT ECRIRE("a" * 2) FIN') == (
        "Opération impossible : « * » entre un texte et un nombre"
    )


def test_erreur_moins_devant_un_texte():
    assert erreur('DEBUT ECRIRE(-"a") FIN') == (
        "Impossible de mettre un signe moins devant un texte"
    )


def test_erreur_mot_reserve_comme_variable():
    assert "réservé" in erreur("DEBUT ECRIRE = 5 FIN")


def test_sortie_vide_en_cas_d_erreur():
    r = executer_code('DEBUT ECRIRE("avant") ECRIRE(z) FIN')
    assert r["output"] == ""
    assert r["error"] == "Variable z non déclarée"




def test_erreur_de_syntaxe():
    r = executer_code("DEBUT ECRIRE( FIN")
    assert r["output"] == ""
    assert "syntaxe" in r["error"]


def test_programme_vide():
    assert "syntaxe" in erreur("")


def test_programme_sans_fin():
    assert "syntaxe" in erreur("DEBUT ECRIRE(1)")


def test_programme_sans_debut():
    assert "syntaxe" in erreur("ECRIRE(1) FIN")


def test_nombre_avec_exposant_refuse_proprement():
    r = executer_code("DEBUT ECRIRE(1e5) FIN")
    assert r["error"] is not None
    assert "interne" not in r["error"]


def test_message_syntaxe_avec_position():
    class Fausse:
        line = 3
        column = 5

    assert message_syntaxe(Fausse()) == "Erreur de syntaxe à la ligne 3, colonne 5"


def test_message_syntaxe_sans_position():
    class Fausse:
        line = -1
        column = -1

    assert "syntaxe" in message_syntaxe(Fausse())




def test_route_run_succes():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(1 + 2) FIN"})
    assert reponse.status_code == 200
    assert reponse.json() == {"output": "3", "error": None}


def test_route_run_erreur_reste_en_200():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(z) FIN"})
    assert reponse.status_code == 200
    assert reponse.json()["error"] == "Variable z non déclarée"