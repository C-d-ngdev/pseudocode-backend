from lark import Token 
class ErreurPseudocode(Exception):
    pass


def interprete(valeur, variable):
    token = valeur.children[0]
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
            result = result / suivant
    return result
        
            
           

       



