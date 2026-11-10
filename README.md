# pseudocode-backend
API et interpréteur de pseudo-code algorithmique en français, construits avec Python, FastAPI et Lark
Ce dépôt contient la partie serveur de la Plateforme de Pseudo Code Algo.

## Fonctionnalités

- Interpréteur de pseudo-code (grammaire définie avec Lark)
- API REST avec FastAPI et documentation Swagger automatique
- Exécution de code via la route `POST /run`
- Tests automatisés avec pytest

## Stack technique

- Python 3.11+
- FastAPI + Uvicorn
- Lark (parser)
- SQLModel + SQLite
- pytest

## Installation

```bash
git clone https://github.com/Mohamed00077/pseudocode-backend.git
cd pseudocode-backend
python -m venv .venv

# Linux / Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Lancer le serveur

```bash
uvicorn app.main:app --reload
```

- API : http://localhost:8000
- Documentation : http://localhost:8000/docs

## Lancer les tests

```bash
pytest
```

## Structure du projet

```
app/
├── main.py          # point d'entrée FastAPI
├── interpreter/     # grammaire et exécution du pseudo-code
├── models/          # modèles de base de données
└── routers/         # routes de l'API
tests/
```

## Exemple d'utilisation

```http
POST /run
{ "code": "DEBUT\n  ECRIRE(\"Bonjour\")\nFIN" }
```

## Dépôt frontend

L'interface web est dans [pseudocode-frontend](https://github.com/Mohamed00077/pseudocode-frontend).

## Contribuer

Les contributions sont les bienvenues : forkez le dépôt, créez une branche, puis ouvrez une Pull Request. Pensez à ajouter des tests pour toute nouvelle instruction du langage.

## Licence

Distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE).
