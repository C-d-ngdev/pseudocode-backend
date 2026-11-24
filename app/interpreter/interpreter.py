import logging
import math
import operator
import re

from lark import Tree
from lark.exceptions import UnexpectedInput

from app.interpreter.parser import parser

logger = logging.getLogger(__name__)

# ---------- Limites de sécurité (la route /run est publique) ----------
MAX_CARACTERES = 10_000        # taille maximale d'un programme
MAX_ITERATIONS = 100_000       # nombre total de répétitions de boucles
MAX_LIGNES = 10_000            # nombre maximal de lignes affichées
MAX_ENTREES = 1_000            # nombre maximal de saisies fournies à LIRE
MAX_LONGUEUR_ENTREE = 1_000    # longueur maximale d'une saisie

MOTS_RESERVES = {
    "DEBUT", "FIN", "ECRIRE", "LIRE",
    "SI", "ALORS", "SINON", "FINSI",
    "POUR", "DE", "PAS", "FAIRE", "FINPOUR",
    "TANT", "QUE", "FINTANTQUE",
    "ET", "OU", "NON",
}

ECHAPPEMENTS = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}

COMPARATEURS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}


class ErreurPseudocode(Exception):
    """Erreur causée par le programme de l'utilisateur (pas par l'interpréteur)."""


class Contexte:
    """État d'une exécution : variables, lignes affichées, répétitions, saisies."""

    def __init__(self, entrees=None):
        self.variables = {}
        self.sortie = []
        self.iterations = 0
        self.entrees = entrees or []
        self.position_entree = 0

    def compter_iteration(self):
        self.iterations += 1
        if self.iterations > MAX_ITERATIONS:
            raise ErreurPseudocode(
                f"Boucle trop longue : plus de {MAX_ITERATIONS} répétitions "
                "(boucle infinie ?)"
            )

    def entree_suivante(self):
        if self.position_entree >= len(self.entrees):
            raise ErreurPseudocode(
                f"Saisie manquante : le programme demande la saisie n°{self.position_entree + 1}, "
                f"mais {len(self.entrees)} saisie(s) seulement ont été fournies"
            )
        valeur = self.entrees[self.position_entree]
        self.position_entree += 1
        return valeur


#  Valeurs et expressions

def est_nombre(valeur):
    return isinstance(valeur, (int, float)) and not isinstance(valeur, bool)


def decrire_type(valeur):
    return "un nombre" if est_nombre(valeur) else "un texte"


def arrondir(valeur):
    """Arrondit les réels à 10 décimales, comme à l'affichage (0.1 + 0.2 == 0.3)."""
    return round(valeur, 10) if isinstance(valeur, float) else valeur


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


#  Conditions

def comparer(operateur, gauche, droite):
    if est_nombre(gauche) != est_nombre(droite):
        raise ErreurPseudocode(
            f"Comparaison impossible : « {operateur} » entre "
            f"{decrire_type(gauche)} et {decrire_type(droite)}"
        )
    if operateur not in COMPARATEURS:
        raise NotImplementedError(f"Comparateur inconnu : {operateur}")
    if est_nombre(gauche):
        gauche, droite = arrondir(gauche), arrondir(droite)
    return COMPARATEURS[operateur](gauche, droite)


def evaluer_comparaison(comparaison, variables):
    gauche = interprete_expression(comparaison.children[0], variables)
    operateur = str(comparaison.children[1].children[0])
    droite = interprete_expression(comparaison.children[2], variables)
    return comparer(operateur, gauche, droite)


def evaluer_condition_non(noeud, variables):
    if noeud.data == "non":
        return not evaluer_condition_non(noeud.children[0], variables)
    if noeud.data == "groupe":
        return evaluer_condition(noeud.children[0], variables)
    if noeud.data == "condition_non":
        return evaluer_comparaison(noeud.children[0], variables)
    raise NotImplementedError(f"Condition inconnue : {noeud.data}")


def evaluer_condition_et(noeud, variables):
    return all(evaluer_condition_non(e, variables) for e in noeud.children)


def evaluer_condition(condition, variables):
    return any(evaluer_condition_et(e, variables) for e in condition.children)


#  Instructions


def verifier_nom_variable(nom):
    if nom in MOTS_RESERVES:
        raise ErreurPseudocode(
            f"« {nom} » est un mot réservé, impossible de l'utiliser comme nom de variable"
        )


def verifier_saisies(entrees):
    """Contrôle les saisies fournies avec le programme (nombre et longueur)."""
    if len(entrees) > MAX_ENTREES:
        raise ErreurPseudocode(f"Trop de saisies (maximum {MAX_ENTREES})")
    for texte in entrees:
        if len(texte) > MAX_LONGUEUR_ENTREE:
            raise ErreurPseudocode(
                f"Une saisie dépasse {MAX_LONGUEUR_ENTREE} caractères"
            )
    return entrees


def convertir_saisie(texte):
    """Une saisie qui ressemble à un nombre devient un nombre, sinon c'est un texte.

    On passe par une expression régulière plutôt que par int()/float() seuls :
    float("nan") et float("inf") sont acceptés par Python, mais pour nous
    ce sont de simples textes.
    """
    propre = texte.strip()
    if re.fullmatch(r"-?[0-9]+(\.[0-9]+)?", propre):
        return convertir_nombre(propre)
    return texte


def executer_affectation(affectation, ctx):
    nom = str(affectation.children[0])
    verifier_nom_variable(nom)
    ctx.variables[nom] = interprete_expression(affectation.children[1], ctx.variables)


def executer_affichage(affichage, ctx):
    if len(ctx.sortie) >= MAX_LIGNES:
        raise ErreurPseudocode(f"Trop de lignes affichées (maximum {MAX_LIGNES})")
    valeur = interprete_expression(affichage.children[0], ctx.variables)
    ctx.sortie.append(formater(valeur))


def executer_lecture(lecture, ctx):
    nom = str(lecture.children[0])
    verifier_nom_variable(nom)
    ctx.variables[nom] = convertir_saisie(ctx.entree_suivante())


def executer_si(noeud, ctx):
    enfants = noeud.children
    for i in range(0, len(enfants) - 1, 2):
        if evaluer_condition(enfants[i], ctx.variables):
            executer_bloc(enfants[i + 1], ctx)
            return
    if len(enfants) % 2 == 1:
        executer_bloc(enfants[-1], ctx)


def executer_pour(noeud, ctx):
    variables = ctx.variables
    nom = str(noeud.children[0])
    verifier_nom_variable(nom)
    debut = interprete_expression(noeud.children[1], variables)
    fin = interprete_expression(noeud.children[2], variables)
    bloc = noeud.children[-1]

    pas = 1
    if len(noeud.children) == 5:
        pas = interprete_expression(noeud.children[3].children[0], variables)

    if not (est_nombre(debut) and est_nombre(fin) and est_nombre(pas)):
        raise ErreurPseudocode(
            "Dans une boucle POUR, le début, la fin et le pas doivent être des nombres"
        )
    if pas == 0:
        raise ErreurPseudocode("Le pas d'une boucle POUR ne peut pas être zéro")

    repetitions = math.floor(round((fin - debut) / pas, 9)) + 1
    for k in range(max(repetitions, 0)):
        ctx.compter_iteration()
        variables[nom] = debut + k * pas
        executer_bloc(bloc, ctx)


def executer_tantque(noeud, ctx):
    condition, bloc = noeud.children
    while evaluer_condition(condition, ctx.variables):
        ctx.compter_iteration()
        executer_bloc(bloc, ctx)


def executer_instruction(instruction, ctx):
    noeud = instruction.children[0]
    if noeud.data == "affectation":
        executer_affectation(noeud, ctx)
    elif noeud.data == "affichage":
        executer_affichage(noeud, ctx)
    elif noeud.data == "lecture":
        executer_lecture(noeud, ctx)
    elif noeud.data == "si":
        executer_si(noeud, ctx)
    elif noeud.data == "pour":
        executer_pour(noeud, ctx)
    elif noeud.data == "tantque":
        executer_tantque(noeud, ctx)
    else:
        raise NotImplementedError(f"Instruction inconnue : {noeud.data}")


def executer_bloc(bloc, ctx):
    for instruction in bloc.children:
        executer_instruction(instruction, ctx)


def executer(arbre, entrees=None):
    ctx = Contexte(entrees)
    for instruction in arbre.children:
        executer_instruction(instruction, ctx)
    return "\n".join(ctx.sortie)



#  Point d'entrée


def message_syntaxe(erreur):
    ligne = getattr(erreur, "line", -1)
    colonne = getattr(erreur, "column", -1)
    if isinstance(ligne, int) and ligne > 0:
        return f"Erreur de syntaxe à la ligne {ligne}, colonne {colonne}"
    return "Erreur de syntaxe : le programme est incomplet ou mal formé"


def executer_code(code, inputs=None):
    if len(code) > MAX_CARACTERES:
        return {
            "output": "",
            "error": f"Programme trop long (maximum {MAX_CARACTERES} caractères)",
        }
    try:
        entrees = verifier_saisies(inputs or [])
        arbre = parser.parse(code)
        return {"output": executer(arbre, entrees), "error": None}
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