from lark import Token 
from lark.exceptions import UnexpectedInput
from app.interpreter.parser import parser
class ErreurPseudocode(Exception):
    pass


def interprete(valeur, variable):
    token = valeur.children[0]
    if not isinstance(token, Token):
        return interprete_expression(token, variable)
    if token.type == "NUMBER":
        if "." in token:
            token_convert = float(token)
            return token_convert
        else:
            token_convert = int(token)  
            return token_convert  
    elif token.type == "ESCAPED_STRING":
        token_convert = token[1:-1]
        return token_convert
    elif token.type == "CNAME":
        if token in variable:
            return variable[token]
        else:
            raise ErreurPseudocode(f"Variable {token} non declarée")   



def interprete_terme(terme, variable):
    result = interprete(terme.children[0], variable)
    for i in range(1, len(terme.children), 2):
        operateur = terme.children[i].children[0]
        suivant = interprete(terme.children[i + 1], variable)
        if operateur == "*":
            result = result * suivant
        else:
            if suivant == 0:
                raise ErreurPseudocode("Tentative de division par zéro !")
            else:
                result = result / suivant
    return result


def interprete_expression(expression, variable):
    result = interprete_terme(expression.children[0], variable)
    for i in range(1, len(expression.children), 2):
        operateur = expression.children[i].children[0]
        suivant = interprete_terme(expression.children[i + 1], variable)
        if operateur =="+":
            result = result + suivant
        else:
            result = result - suivant    
    return result


def executer_affectation(affectation, variable):
    name = str(affectation.children[0])
    valeur = interprete_expression(affectation.children[1], variable)    
    variable[name] = valeur


def executer_affichage(affichage, variable, sortie):
    valeur = interprete_expression(affichage.children[0], variable)
    valeur = str(valeur)
    sortie.append(valeur)


def executer(tree):
    variables = {}
    sortie = []
    for instruction in tree.children:
        noeud = instruction.children[0]
        if noeud.data == "affectation":
            executer_affectation(noeud, variables)
        else:
            executer_affichage(noeud, variables, sortie)
    return "\n".join(sortie)


def executer_code(code):
    try:
        tree = parser.parse(code)
        sortie = executer(tree)
        return {"output": sortie, "error": None}
    except ErreurPseudocode as e:
        return {"output": "", "error": str(e)}
    except UnexpectedInput:
        return {"output": "", "error": "Erreur de syntaxe"}
    except Exception:
        return {"output": "", "error": "Erreur interne de l'interpréteur"}    
        
            
           

       



