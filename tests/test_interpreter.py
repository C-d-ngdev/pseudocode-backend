import pytest
from fastapi.testclient import TestClient

from app.interpreter.interpreter import executer_code, message_syntaxe
from app.main import app

client = TestClient(app)


def sortie(code):
    return executer_code(code)["output"]


def erreur(code):
    return executer_code(code)["error"]


def vrai_ou_faux(condition):
    """Renvoie True si la condition est vraie, False sinon."""
    code = f'DEBUT SI {condition} ALORS ECRIRE("V") SINON ECRIRE("F") FINSI FIN'
    resultat = sortie(code)
    assert resultat in ("V", "F"), executer_code(code)
    return resultat == "V"


# =====================================================================
#  Affichage, affectation, calculs
# =====================================================================

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


def test_variable_d_une_seule_lettre_majuscule_autorisee():
    assert sortie("DEBUT A = 5 ECRIRE(A) FIN") == "5"


# =====================================================================
#  Conditions : SI / SINON / SINON SI
# =====================================================================

def test_si_vrai():
    assert sortie('DEBUT SI 3 > 2 ALORS ECRIRE("oui") FINSI FIN') == "oui"


def test_si_faux_sans_sinon():
    r = executer_code('DEBUT ECRIRE("a") SI 1 > 2 ALORS ECRIRE("b") FINSI FIN')
    assert r == {"output": "a", "error": None}


def test_si_sinon():
    code = 'DEBUT SI 1 > 2 ALORS ECRIRE("a") SINON ECRIRE("b") FINSI FIN'
    assert sortie(code) == "b"


def test_si_avec_plusieurs_instructions():
    code = """DEBUT
  SI 1 < 2 ALORS
    x = 1
    y = x + 1
    ECRIRE(y)
  FINSI
FIN"""
    assert sortie(code) == "2"


@pytest.mark.parametrize(
    "condition, attendu",
    [
        ("1 == 1", True), ("1 == 2", False),
        ("1 != 2", True), ("1 != 1", False),
        ("1 < 2", True), ("2 < 1", False),
        ("2 > 1", True), ("1 > 2", False),
        ("2 <= 2", True), ("3 <= 2", False),
        ("2 >= 2", True), ("1 >= 2", False),
    ],
)
def test_comparateurs(condition, attendu):
    assert vrai_ou_faux(condition) is attendu


def test_comparaison_avec_nombre_negatif():
    assert sortie('DEBUT x = -7 SI x < -5 ALORS ECRIRE("bas") FINSI FIN') == "bas"


def test_comparaison_avec_calculs_et_variables():
    assert vrai_ou_faux("2 + 3 * 4 == 14") is True
    code = 'DEBUT n = 4 SI n * 2 > n + 3 ALORS ECRIRE("V") SINON ECRIRE("F") FINSI FIN'
    assert sortie(code) == "V"


def test_comparaison_de_textes():
    assert vrai_ou_faux('"a" == "a"') is True
    assert vrai_ou_faux('"a" != "b"') is True
    assert vrai_ou_faux('"a" < "b"') is True
    assert vrai_ou_faux('"b" < "a"') is False


def test_comparaison_de_reels_coherente_avec_l_affichage():
    assert vrai_ou_faux("0.1 + 0.2 == 0.3") is True


@pytest.mark.parametrize(
    "condition, attendu",
    [
        ("1 == 1 ET 2 == 2", True),
        ("1 == 1 ET 2 == 3", False),
        ("1 == 2 OU 2 == 2", True),
        ("1 == 2 OU 2 == 3", False),
        ("NON 1 == 2", True),
        ("NON 1 == 1", False),
        ("NON NON 1 == 1", True),
        # ET est prioritaire sur OU
        ("1 == 1 OU 1 == 2 ET 1 == 3", True),
        ("(1 == 1 OU 1 == 2) ET 1 == 3", False),
        # parenthèses de conditions et parenthèses de calcul
        ("NON (1 == 2 OU 2 == 3)", True),
        ("((1 < 2) ET (2 < 3)) OU 5 == 6", True),
        ("(1 + 1) * 2 == 4", True),
    ],
)
def test_conditions_combinees(condition, attendu):
    assert vrai_ou_faux(condition) is attendu


def test_et_s_arrete_a_la_premiere_condition_fausse():
    # La division par zéro n'est jamais évaluée
    code = """DEBUT
  x = 0
  SI x != 0 ET 10 / x > 1 ALORS ECRIRE("oui") SINON ECRIRE("non") FINSI
FIN"""
    assert executer_code(code) == {"output": "non", "error": None}


def test_ou_s_arrete_a_la_premiere_condition_vraie():
    code = """DEBUT
  x = 0
  SI x == 0 OU 10 / x > 1 ALORS ECRIRE("oui") SINON ECRIRE("non") FINSI
FIN"""
    assert executer_code(code) == {"output": "oui", "error": None}


@pytest.mark.parametrize(
    "x, attendu",
    [(-1, "negatif"), (0, "zero"), (5, "petit"), (50, "grand")],
)
def test_sinon_si_enchaines(x, attendu):
    code = f"""DEBUT
  x = {x}
  SI x < 0 ALORS ECRIRE("negatif")
  SINON SI x == 0 ALORS ECRIRE("zero")
  SINON SI x < 10 ALORS ECRIRE("petit")
  SINON ECRIRE("grand")
  FINSI
FIN"""
    assert executer_code(code) == {"output": attendu, "error": None}


# =====================================================================
#  Conditions imbriquées
# =====================================================================

@pytest.mark.parametrize(
    "a, b, c, attendu",
    [
        (1, 1, 1, "a b c"),
        (1, 1, 0, "a b non-c"),
        (1, 0, 1, "a non-b"),
        (0, 1, 1, "non-a"),
    ],
)
def test_trois_si_imbriques(a, b, c, attendu):
    code = f"""DEBUT
  a = {a}
  b = {b}
  c = {c}
  SI a == 1 ALORS
    SI b == 1 ALORS
      SI c == 1 ALORS
        ECRIRE("a b c")
      SINON
        ECRIRE("a b non-c")
      FINSI
    SINON
      ECRIRE("a non-b")
    FINSI
  SINON
    ECRIRE("non-a")
  FINSI
FIN"""
    assert executer_code(code) == {"output": attendu, "error": None}


def test_si_dans_un_sinon_avec_deux_finsi():
    code = """DEBUT
  SI 1 > 2 ALORS
    ECRIRE("a")
  SINON
    SI 2 > 1 ALORS
      ECRIRE("b")
    FINSI
  FINSI
FIN"""
    assert sortie(code) == "b"


def test_si_dans_une_boucle_dans_un_si():
    code = """DEBUT
  SI 1 == 1 ALORS
    POUR i DE 1 A 4 FAIRE
      SI i > 1 ET i < 4 ALORS
        ECRIRE(i)
      FINSI
    FINPOUR
  FINSI
FIN"""
    assert sortie(code) == "2\n3"


# =====================================================================
#  Comparaisons impossibles (nombre contre texte)
# =====================================================================

@pytest.mark.parametrize(
    "condition, message",
    [
        ('1 == "a"', "Comparaison impossible : « == » entre un nombre et un texte"),
        ('1 != "a"', "Comparaison impossible : « != » entre un nombre et un texte"),
        ('"a" < 1', "Comparaison impossible : « < » entre un texte et un nombre"),
        ('"a" >= 1', "Comparaison impossible : « >= » entre un texte et un nombre"),
    ],
)
def test_erreur_comparaison_nombre_et_texte(condition, message):
    r = executer_code(f"DEBUT SI {condition} ALORS ECRIRE(1) FINSI FIN")
    assert r == {"output": "", "error": message}


def test_erreur_comparaison_avec_variables():
    code = 'DEBUT n = 5 t = "5" SI n == t ALORS ECRIRE("egal") FINSI FIN'
    assert erreur(code) == "Comparaison impossible : « == » entre un nombre et un texte"


def test_erreur_comparaison_dans_tant_que():
    code = 'DEBUT TANT QUE 1 < "a" FAIRE ECRIRE(1) FINTANTQUE FIN'
    assert "Comparaison impossible" in erreur(code)


def test_erreur_variable_non_declaree_dans_une_condition():
    assert erreur("DEBUT SI z > 1 ALORS ECRIRE(1) FINSI FIN") == "Variable z non déclarée"


# =====================================================================
#  Boucle POUR (PAS facultatif)
# =====================================================================

def test_pour_sans_pas():
    code = "DEBUT POUR i DE 1 A 3 FAIRE ECRIRE(i) FINPOUR FIN"
    assert sortie(code) == "1\n2\n3"


def test_pour_somme():
    code = """DEBUT
  somme = 0
  POUR i DE 1 A 5 FAIRE
    somme = somme + i
  FINPOUR
  ECRIRE(somme)
FIN"""
    assert sortie(code) == "15"


def test_pour_avec_pas():
    code = "DEBUT POUR i DE 1 A 10 PAS 3 FAIRE ECRIRE(i) FINPOUR FIN"
    assert sortie(code) == "1\n4\n7\n10"


def test_pour_avec_pas_negatif():
    code = "DEBUT POUR i DE 5 A 1 PAS -2 FAIRE ECRIRE(i) FINPOUR FIN"
    assert sortie(code) == "5\n3\n1"


def test_pour_sans_pas_quand_debut_depasse_fin():
    code = 'DEBUT ECRIRE("a") POUR i DE 5 A 1 FAIRE ECRIRE(i) FINPOUR FIN'
    assert executer_code(code) == {"output": "a", "error": None}


def test_pour_avec_bornes_calculees():
    code = "DEBUT n = 2 POUR i DE n A n * 2 FAIRE ECRIRE(i) FINPOUR FIN"
    assert sortie(code) == "2\n3\n4"


def test_pour_avec_pas_reel():
    code = "DEBUT POUR x DE 0 A 0.3 PAS 0.1 FAIRE ECRIRE(x) FINPOUR FIN"
    assert len(sortie(code).split("\n")) == 4


def test_pour_variable_garde_sa_derniere_valeur():
    code = "DEBUT POUR i DE 1 A 3 FAIRE ECRIRE(i) FINPOUR ECRIRE(i) FIN"
    assert sortie(code) == "1\n2\n3\n3"


def test_pour_modifier_la_variable_ne_change_pas_les_repetitions():
    code = "DEBUT POUR i DE 1 A 3 FAIRE i = 10 ECRIRE(i) FINPOUR FIN"
    assert sortie(code) == "10\n10\n10"


def test_pour_imbriques():
    code = """DEBUT
  POUR i DE 1 A 2 FAIRE
    POUR j DE 1 A 2 FAIRE
      ECRIRE(i * 10 + j)
    FINPOUR
  FINPOUR
FIN"""
    assert sortie(code) == "11\n12\n21\n22"


def test_erreur_pour_pas_zero():
    code = "DEBUT POUR i DE 1 A 3 PAS 0 FAIRE ECRIRE(i) FINPOUR FIN"
    assert erreur(code) == "Le pas d'une boucle POUR ne peut pas être zéro"


def test_erreur_pour_bornes_non_numeriques():
    code = 'DEBUT POUR i DE 1 A "a" FAIRE ECRIRE(i) FINPOUR FIN'
    assert erreur(code) == (
        "Dans une boucle POUR, le début, la fin et le pas doivent être des nombres"
    )


# =====================================================================
#  Boucle TANT QUE
# =====================================================================

def test_tant_que_compte_a_rebours():
    code = """DEBUT
  n = 3
  TANT QUE n > 0 FAIRE
    ECRIRE(n)
    n = n - 1
  FINTANTQUE
FIN"""
    assert sortie(code) == "3\n2\n1"


def test_tant_que_condition_fausse_des_le_depart():
    code = 'DEBUT ECRIRE("a") TANT QUE 1 > 2 FAIRE ECRIRE("b") FINTANTQUE FIN'
    assert sortie(code) == "a"


def test_tant_que_avec_et_ou_non():
    code = """DEBUT
  i = 0
  TANT QUE i < 10 ET NON i == 3 FAIRE
    i = i + 1
  FINTANTQUE
  ECRIRE(i)
FIN"""
    assert sortie(code) == "3"


# =====================================================================
#  Protections (la route /run est publique)
# =====================================================================

def test_boucle_infinie_est_arretee():
    code = "DEBUT x = 1 TANT QUE 1 < 2 FAIRE x = x + 1 FINTANTQUE FIN"
    r = executer_code(code)
    assert r["output"] == ""
    assert "Boucle trop longue" in r["error"]


def test_boucles_imbriquees_trop_longues():
    code = """DEBUT
  POUR i DE 1 A 1000 FAIRE
    POUR j DE 1 A 1000 FAIRE
      x = 1
    FINPOUR
  FINPOUR
FIN"""
    assert "Boucle trop longue" in erreur(code)


def test_trop_de_lignes_affichees():
    code = "DEBUT POUR i DE 1 A 20000 FAIRE ECRIRE(i) FINPOUR FIN"
    assert "Trop de lignes affichées" in erreur(code)


def test_programme_trop_long():
    code = "DEBUT " + "ECRIRE(1) " * 2000 + "FIN"
    assert "Programme trop long" in erreur(code)


# =====================================================================
#  Erreurs du programme (messages exacts)
# =====================================================================

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


@pytest.mark.parametrize("mot", ["ECRIRE", "ALORS", "FINSI", "SINON"])
def test_erreur_mot_reserve_comme_variable(mot):
    assert "réservé" in erreur(f"DEBUT {mot} = 5 FIN")


def test_sortie_vide_en_cas_d_erreur():
    r = executer_code('DEBUT ECRIRE("avant") ECRIRE(z) FIN')
    assert r["output"] == ""
    assert r["error"] == "Variable z non déclarée"


# =====================================================================
#  Erreurs de syntaxe
# =====================================================================

def test_erreur_de_syntaxe():
    r = executer_code("DEBUT ECRIRE( FIN")
    assert r["output"] == ""
    assert "syntaxe" in r["error"]


@pytest.mark.parametrize(
    "code",
    [
        "",
        "DEBUT ECRIRE(1)",
        "ECRIRE(1) FIN",
        "DEBUT SI 1 == 1 ALORS ECRIRE(1) FIN",
        "DEBUT SI 1 == 1 ECRIRE(1) FINSI FIN",
        "DEBUT POUR i DE 1 A 3 ECRIRE(i) FINPOUR FIN",
        "DEBUT TANT QUE 1 < 2 FAIRE ECRIRE(1) FIN",
        "DEBUT SI 1 == 1 ALORS FINSI FIN",
        "DEBUT SI 1 ALORS ECRIRE(1) FINSI FIN",
    ],
)
def test_programmes_mal_formes(code):
    assert "syntaxe" in erreur(code)


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


# =====================================================================
#  Route /run
# =====================================================================

def test_route_run_succes():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(1 + 2) FIN"})
    assert reponse.status_code == 200
    assert reponse.json() == {"output": "3", "error": None}


def test_route_run_erreur_reste_en_200():
    reponse = client.post("/run", json={"code": "DEBUT ECRIRE(z) FIN"})
    assert reponse.status_code == 200
    assert reponse.json()["error"] == "Variable z non déclarée"


def test_route_run_avec_condition_et_boucle():
    code = "DEBUT POUR i DE 1 A 3 FAIRE SI i != 2 ALORS ECRIRE(i) FINSI FINPOUR FIN"
    reponse = client.post("/run", json={"code": code})
    assert reponse.status_code == 200
    assert reponse.json() == {"output": "1\n3", "error": None}