import logging
import math
import re

from lark import Token, Tree
from lark.exceptions import UnexpectedInput

from app.interpreter.parser import parser

logger = logging.getLogger(__name__)

MOTS_RESERVES = {"DEBUT", "FIN", "ECRIRE"}

ECHAPPEMENTS = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


class ErreurPseudocode(Exception):
    """Erreur causée par le programme de l'utilisateur (pas par l'interpréteur)."""


def est_nombre(valeur):
    return isinstance(valeur, (int, float)) and not isinstance(valeur, bool)


def decrire_type(valeur):
    return "un nombre" if est_nombre(valeur) else "un texte"


def convertir_texte(token):
    """Retire les guillemets et traduit \\n, \\t, \\" et \\\\."""
    contenu = token[1:-1]
    return re.sub(
        r"\\(.)",
        lambda m: ECHAPPEMENTS.get(m.group(1), m.group(0)),
        contenu,
        flags=re.DOTALL,
    )


def convertir_nombre(token):
    if "." in token:
        nombre = float(token)
        if math.isinf(nombre):
            raise ErreurPseudocode("Nombre trop grand")
        return nombre
    return int(token)


def formater(valeur):
    """Texte affiché pour une valeur. Les réels sont arrondis à 10 décimales."""
    if isinstance(valeur, float):
        return str(round(valeur, 10))
    return str(valeur)


def appliquer_operation(operateur, gauche, droite):
    if operateur == "+" and isinstance(gauche, str) and isinstance(droite, str):
        return gauche + droite

    if not (est_nombre(gauche) and est_nombre(droite)):
        raise ErreurPseudocode(
            f"Opération impossible : « {operateur} » entre "
            f"{decrire_type(gauche)} et {decrire_type(droite)}"
        )

    if operateur == "+":
        return gauche + droite
    if operateur == "-":
        return gauche - droite
    if operateur == "*":
        return gauche * droite
    if operateur == "/":
        if droite == 0:
            raise ErreurPseudocode("Division par zéro")
        return gauche / droite

    raise NotImplementedError(f"Opérateur inconnu : {operateur}")


def interprete(valeur, variables):
    if valeur.data == "negation":
        operande = interprete(valeur.children[0], variables)
        if not est_nombre(operande):
            raise ErreurPseudocode("Impossible de mettre un signe moins devant un texte")
        return -operande

    element = valeur.children[0]

    if isinstance(element, Tree):
        return interprete_expression(element, variables)

    if element.type == "NOMBRE":
        return convertir_nombre(element)
    if element.type == "ESCAPED_STRING":
        return convertir_texte(element)
    if element.type == "CNAME":
        if element not in variables:
            raise ErreurPseudocode(f"Variable {element} non déclarée")
        return variables[element]

    raise NotImplementedError(f"Type de valeur inconnu : {element.type}")


def interprete_terme(terme, variables):
    resultat = interprete(terme.children[0], variables)
    for i in range(1, len(terme.children), 2):
        operateur = terme.children[i].children[0]
        suivant = interprete(terme.children[i + 1], variables)
        resultat = appliquer_operation(operateur, resultat, suivant)
    return resultat


def interprete_expression(expression, variables):
    resultat = interprete_terme(expression.children[0], variables)
    for i in range(1, len(expression.children), 2):
        operateur = expression.children[i].children[0]
        suivant = interprete_terme(expression.children[i + 1], variables)
        resultat = appliquer_operation(operateur, resultat, suivant)
    return resultat


def executer_affectation(affectation, variables):
    nom = str(affectation.children[0])
    if nom in MOTS_RESERVES:
        raise ErreurPseudocode(
            f"« {nom} » est un mot réservé, impossible de l'utiliser comme nom de variable"
        )
    variables[nom] = interprete_expression(affectation.children[1], variables)


def executer_affichage(affichage, variables, sortie):
    valeur = interprete_expression(affichage.children[0], variables)
    sortie.append(formater(valeur))


def executer(arbre):
    variables = {}
    sortie = []
    for instruction in arbre.children:
        noeud = instruction.children[0]
        if noeud.data == "affectation":
            executer_affectation(noeud, variables)
        elif noeud.data == "affichage":
            executer_affichage(noeud, variables, sortie)
        else:
            raise NotImplementedError(f"Instruction inconnue : {noeud.data}")
    return "\n".join(sortie)


def message_syntaxe(erreur):
    ligne = getattr(erreur, "line", -1)
    colonne = getattr(erreur, "column", -1)
    if isinstance(ligne, int) and ligne > 0:
        return f"Erreur de syntaxe à la ligne {ligne}, colonne {colonne}"
    return "Erreur de syntaxe : le programme est incomplet ou mal formé"


def executer_code(code):
    try:
        arbre = parser.parse(code)
        return {"output": executer(arbre), "error": None}
    except ErreurPseudocode as erreur:
        return {"output": "", "error": str(erreur)}
    except UnexpectedInput as erreur:
        return {"output": "", "error": message_syntaxe(erreur)}
    except RecursionError:
        return {"output": "", "error": "Programme trop complexe (trop d'imbrications)"}
    except OverflowError:
        return {"output": "", "error": "Nombre trop grand"}
    except Exception:
        logger.exception("Erreur interne pendant l'exécution du pseudo-code")
        return {"output": "", "error": "Erreur interne de l'interpréteur"}