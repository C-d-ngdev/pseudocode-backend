from typing import Annotated

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.interpreter.exemples import EXEMPLES
from app.interpreter.interpreter import (
    MAX_CARACTERES,
    MAX_ENTREES,
    MAX_ITERATIONS,
    MAX_LIGNES,
    MAX_LONGUEUR_ENTREE,
    executer_code,
)

DESCRIPTION = rf"""
API d'exécution de **pseudo-code algorithmique en français**.

Envoyez un programme à `POST /run` : la réponse contient toujours `output`
(le texte affiché) et `error` (un message d'erreur, ou `null`).
Les erreurs de pseudo-code sont renvoyées avec un statut **200** : lisez le champ `error`.

## Aide-mémoire de la syntaxe

| Besoin | Syntaxe |
|---|---|
| Programme | `DEBUT ... FIN` |
| Afficher | `ECRIRE(expression)` |
| Lire une saisie | `LIRE(x)` |
| Affecter | `x <- 5` ou `x = 5` |
| Condition | `SI c ALORS ... SINON SI c ALORS ... SINON ... FINSI` |
| Boucle avec compteur | `POUR i DE 1 A 10 PAS 2 FAIRE ... FINPOUR` (PAS facultatif) |
| Boucle conditionnelle | `TANT QUE c FAIRE ... FINTANTQUE` |

- Comparateurs : `==` `!=` `<` `>` `<=` `>=`
- Logique : `ET` `OU` `NON`, avec parenthèses
- Calculs : `+` `-` `*` `/` (la division donne toujours un réel)

## Règles

- Les mots-clés s'écrivent en **majuscules**.
- Les nombres décimaux s'écrivent avec un **point** (`3.5`).
- Les textes s'écrivent entre guillemets doubles ; `\n`, `\t`, `\"` et `\\` sont reconnus.
- On ne peut pas comparer un nombre et un texte.
- Le signe `+` assemble deux textes ; les autres opérations ne concernent que les nombres.
- Dans `POUR`, le pas est facultatif (1 par défaut), peut être négatif, mais pas nul.
- Les structures (`SI`, `POUR`, `TANT QUE`) peuvent s'imbriquer.

## Saisies (`LIRE`)

- `LIRE(x)` range la saisie suivante dans `x`.
- Les saisies sont envoyées dans le champ facultatif `inputs`, **dans l'ordre**, sous forme de **textes**
  (par exemple `["Awa", "20"]`, pas `[20]`).
- Une saisie qui ressemble à un nombre devient un nombre, toute autre saisie reste un texte.
- Si le programme demande plus de saisies que `inputs` n'en contient, une erreur est renvoyée.
  Les saisies en trop sont ignorées.

## Limites

- {MAX_CARACTERES} caractères par programme
- {MAX_ITERATIONS} répétitions de boucle au total
- {MAX_LIGNES} lignes affichées
- {MAX_ENTREES} saisies au maximum, de {MAX_LONGUEUR_ENTREE} caractères chacune

Pour essayer : ouvrez `POST /run`, cliquez sur **Try it out**, choisissez un
exemple dans la liste déroulante, puis **Execute**.
"""

TAGS = [
    {"name": "Exécution", "description": "Exécuter un programme de pseudo-code."},
    {"name": "Santé", "description": "Vérifier que le service répond."},
]

app = FastAPI(
    title="Plateforme Pseudo-code",
    version="0.3.0",
    description=DESCRIPTION,
    openapi_tags=TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeIn(BaseModel):
    code: str = Field(
        description="Programme de pseudo-code à exécuter (de DEBUT à FIN)."
    )
    inputs: list[str] = Field(
        default_factory=list,
        description=(
            "Saisies consommées dans l'ordre par les instructions LIRE. "
            'Envoyez-les sous forme de textes (par exemple ["21"], pas [21]).'
        ),
    )


class ReponseRun(BaseModel):
    output: str = Field(
        description="Texte affiché par le programme, une ligne par ECRIRE (vide en cas d'erreur)."
    )
    error: str | None = Field(
        default=None,
        description="Message d'erreur en français, ou null si tout s'est bien passé.",
    )


def corps_exemple(exemple):
    """Corps JSON d'un exemple : `inputs` n'apparaît que pour les exemples qui en ont."""
    corps = {"code": exemple["code"]}
    if "inputs" in exemple:
        corps["inputs"] = exemple["inputs"]
    return corps


EXEMPLES_REQUETE = {
    exemple["cle"]: {
        "summary": exemple["titre"],
        "description": exemple["description"],
        "value": corps_exemple(exemple),
    }
    for exemple in EXEMPLES
}


REPONSES_RUN = {
    200: {
        "description": (
            "Résultat de l'exécution. En cas d'erreur dans le pseudo-code, "
            "le statut reste 200 et le champ `error` est renseigné."
        ),
        "content": {
            "application/json": {
                "examples": {
                    "succes": {
                        "summary": "Exécution réussie",
                        "value": {"output": "Bonjour\n42", "error": None},
                    },
                    "erreur": {
                        "summary": "Erreur dans le programme",
                        "value": {"output": "", "error": "Variable total non déclarée"},
                    },
                }
            }
        },
    }
}


@app.get("/health", tags=["Santé"], summary="Vérifier que l'API répond")
def health():
    return {"status": "ok"}


@app.post(
    "/run",
    response_model=ReponseRun,
    tags=["Exécution"],
    summary="Exécuter un programme de pseudo-code",
    description=(
        "Exécute le programme et renvoie sa sortie ou un message d'erreur. "
        "Choisissez un exemple dans la liste déroulante du corps de la requête."
    ),
    responses=REPONSES_RUN,
)
def run(payload: Annotated[CodeIn, Body(openapi_examples=EXEMPLES_REQUETE)]):
    return executer_code(payload.code, payload.inputs)