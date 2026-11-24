"""Exemples de pseudo-code affichés dans la documentation (/docs).

Chaque exemple contient :
- cle         : identifiant unique (sans espace)
- titre       : nom affiché dans la liste déroulante
- description : phrase d'explication
- code        : le programme
- inputs      : (facultatif) les saisies envoyées à LIRE, dans l'ordre
- sortie      : la sortie attendue ("" en cas d'erreur)
- erreur      : le message d'erreur attendu (ou un début de message), None si tout va bien

Le test tests/test_examples.py exécute chaque exemple : la documentation
ne peut donc pas devenir fausse sans que pytest le signale.
"""

EXEMPLES = [
    {
        "cle": "affichage",
        "titre": "Affichage",
        "description": "ECRIRE affiche un texte (entre guillemets) ou un nombre. Chaque ECRIRE produit une ligne.",
        "code": """DEBUT
  ECRIRE("Bonjour")
  ECRIRE(42)
FIN""",
        "sortie": "Bonjour\n42",
        "erreur": None,
    },
    {
        "cle": "variables",
        "titre": "Variables et affectation",
        "description": "On affecte avec <- ou =. Le signe + assemble deux textes ou additionne deux nombres.",
        "code": """DEBUT
  nom <- "Awa"
  age = 17
  ECRIRE("Bonjour " + nom)
  ECRIRE(age + 1)
FIN""",
        "sortie": "Bonjour Awa\n18",
        "erreur": None,
    },
    {
        "cle": "lecture",
        "titre": "Lire une saisie (LIRE)",
        "description": "LIRE(x) range la saisie suivante dans x. Les saisies sont envoyées dans le champ inputs, dans l'ordre. Une saisie qui ressemble à un nombre devient un nombre, sinon c'est un texte.",
        "code": """DEBUT
  LIRE(prenom)
  LIRE(age)
  ECRIRE("Bonjour " + prenom)
  ECRIRE(age + 1)
FIN""",
        "inputs": ["Awa", "20"],
        "sortie": "Bonjour Awa\n21",
        "erreur": None,
    },
    {
        "cle": "lecture_boucle",
        "titre": "LIRE dans une boucle",
        "description": "Chaque passage dans la boucle consomme la saisie suivante.",
        "code": """DEBUT
  total <- 0
  POUR i DE 1 A 3 FAIRE
    LIRE(nombre)
    total <- total + nombre
  FINPOUR
  ECRIRE(total)
FIN""",
        "inputs": ["10", "20", "12.5"],
        "sortie": "42.5",
        "erreur": None,
    },
    {
        "cle": "calculs",
        "titre": "Calculs et priorités",
        "description": "Les priorités habituelles s'appliquent. La division donne toujours un réel (10 / 2 donne 5.0).",
        "code": """DEBUT
  ECRIRE(2 + 3 * 4)
  ECRIRE((2 + 3) * 4)
  ECRIRE(7 / 2)
  ECRIRE(10 / 2)
  ECRIRE(-5 + 8)
FIN""",
        "sortie": "14\n20\n3.5\n5.0\n3",
        "erreur": None,
    },
    {
        "cle": "si_sinon",
        "titre": "Condition SI / SINON",
        "description": "Comparateurs : == != < > <= >=. Le SINON est facultatif.",
        "code": """DEBUT
  note <- 12
  SI note >= 10 ALORS
    ECRIRE("Admis")
  SINON
    ECRIRE("Refusé")
  FINSI
FIN""",
        "sortie": "Admis",
        "erreur": None,
    },
    {
        "cle": "sinon_si",
        "titre": "SINON SI enchaînés",
        "description": "Plusieurs conditions à la suite, avec un seul FINSI.",
        "code": """DEBUT
  note <- 15
  SI note < 10 ALORS
    ECRIRE("Insuffisant")
  SINON SI note < 14 ALORS
    ECRIRE("Passable")
  SINON SI note < 16 ALORS
    ECRIRE("Bien")
  SINON
    ECRIRE("Très bien")
  FINSI
FIN""",
        "sortie": "Bien",
        "erreur": None,
    },
    {
        "cle": "et_ou_non",
        "titre": "Conditions avec ET, OU, NON",
        "description": "ET est prioritaire sur OU. Les parenthèses permettent de regrouper des conditions.",
        "code": """DEBUT
  age <- 20
  permis <- "oui"
  SI age >= 18 ET permis == "oui" ALORS
    ECRIRE("Peut conduire")
  FINSI
  SI NON (age < 18 OU permis != "oui") ALORS
    ECRIRE("Même résultat avec NON")
  FINSI
FIN""",
        "sortie": "Peut conduire\nMême résultat avec NON",
        "erreur": None,
    },
    {
        "cle": "si_imbriques",
        "titre": "SI imbriqués",
        "description": "Un SI peut contenir d'autres SI, à tous les niveaux.",
        "code": """DEBUT
  a <- 5
  b <- 8
  SI a > 0 ALORS
    SI b > a ALORS
      ECRIRE("a est positif et b est plus grand")
    SINON
      ECRIRE("a est positif, b n'est pas plus grand")
    FINSI
  SINON
    ECRIRE("a n'est pas positif")
  FINSI
FIN""",
        "sortie": "a est positif et b est plus grand",
        "erreur": None,
    },
    {
        "cle": "pour",
        "titre": "Boucle POUR",
        "description": "POUR variable DE début A fin FAIRE ... FINPOUR. Le pas vaut 1 par défaut.",
        "code": """DEBUT
  somme <- 0
  POUR i DE 1 A 5 FAIRE
    somme <- somme + i
  FINPOUR
  ECRIRE("Somme de 1 à 5 :")
  ECRIRE(somme)
FIN""",
        "sortie": "Somme de 1 à 5 :\n15",
        "erreur": None,
    },
    {
        "cle": "pour_pas",
        "titre": "Boucle POUR avec PAS",
        "description": "Le PAS est facultatif. Il peut être négatif pour compter à l'envers, mais pas nul.",
        "code": """DEBUT
  ECRIRE("Pas de 2 :")
  POUR i DE 0 A 6 PAS 2 FAIRE
    ECRIRE(i)
  FINPOUR
  ECRIRE("Compte à rebours :")
  POUR i DE 3 A 1 PAS -1 FAIRE
    ECRIRE(i)
  FINPOUR
FIN""",
        "sortie": "Pas de 2 :\n0\n2\n4\n6\nCompte à rebours :\n3\n2\n1",
        "erreur": None,
    },
    {
        "cle": "tant_que",
        "titre": "Boucle TANT QUE",
        "description": "TANT QUE condition FAIRE ... FINTANTQUE : répète tant que la condition est vraie.",
        "code": """DEBUT
  n <- 3
  TANT QUE n > 0 FAIRE
    ECRIRE(n)
    n <- n - 1
  FINTANTQUE
  ECRIRE("Décollage !")
FIN""",
        "sortie": "3\n2\n1\nDécollage !",
        "erreur": None,
    },
    {
        "cle": "boucle_et_condition",
        "titre": "Condition dans une boucle",
        "description": "Boucles et conditions se combinent librement.",
        "code": """DEBUT
  POUR i DE 1 A 10 FAIRE
    SI i == 3 OU i == 7 ALORS
      ECRIRE(i)
    FINSI
  FINPOUR
FIN""",
        "sortie": "3\n7",
        "erreur": None,
    },
    {
        "cle": "erreur_variable",
        "titre": "Erreur : variable non déclarée",
        "description": "Une variable doit recevoir une valeur avant d'être utilisée.",
        "code": """DEBUT
  ECRIRE(total)
FIN""",
        "sortie": "",
        "erreur": "Variable total non déclarée",
    },
    {
        "cle": "erreur_saisie_manquante",
        "titre": "Erreur : saisie manquante",
        "description": "Ici LIRE demande une saisie, mais le champ inputs est vide.",
        "code": """DEBUT
  LIRE(age)
  ECRIRE(age)
FIN""",
        "sortie": "",
        "erreur": "Saisie manquante",
    },
    {
        "cle": "erreur_comparaison",
        "titre": "Erreur : nombre comparé à un texte",
        "description": "On ne peut pas comparer un nombre et un texte (17 et \"17\" sont de types différents).",
        "code": """DEBUT
  age <- 17
  SI age == "17" ALORS
    ECRIRE("égal")
  FINSI
FIN""",
        "sortie": "",
        "erreur": "Comparaison impossible : « == » entre un nombre et un texte",
    },
    {
        "cle": "erreur_types",
        "titre": "Erreur : texte et nombre mélangés",
        "description": "Le signe + n'assemble que deux textes ou n'additionne que deux nombres.",
        "code": """DEBUT
  ECRIRE("Total : " + 5)
FIN""",
        "sortie": "",
        "erreur": "Opération impossible : « + » entre un texte et un nombre",
    },
    {
        "cle": "erreur_division",
        "titre": "Erreur : division par zéro",
        "description": "Diviser par zéro arrête le programme avec un message clair.",
        "code": """DEBUT
  ECRIRE(10 / 0)
FIN""",
        "sortie": "",
        "erreur": "Division par zéro",
    },
    {
        "cle": "erreur_boucle_infinie",
        "titre": "Erreur : boucle infinie",
        "description": "Une boucle qui ne s'arrête jamais est interrompue après un nombre maximal de répétitions.",
        "code": """DEBUT
  n <- 1
  TANT QUE n > 0 FAIRE
    n <- n + 1
  FINTANTQUE
FIN""",
        "sortie": "",
        "erreur": "Boucle trop longue",
    },
    {
        "cle": "erreur_syntaxe",
        "titre": "Erreur : syntaxe incorrecte",
        "description": "Ici, la parenthèse de ECRIRE n'est pas refermée.",
        "code": """DEBUT
  ECRIRE("Bonjour"
FIN""",
        "sortie": "",
        "erreur": "Erreur de syntaxe",
    },
]