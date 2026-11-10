# Pseudocode Backend

API de la Plateforme de Pseudo Code Algo : interpréteur de pseudo-code
algorithmique en français et gestion des cours.

Interface web : [pseudocode-frontend](https://github.com/Mohamed00077/pseudocode-frontend)

## Fonctionnalités

- Interpréteur de pseudo-code (grammaire définie avec Lark)
- Exécution de code via `POST /run`
- Gestion des cours et des leçons (contenu en Markdown)
- API REST avec documentation Swagger automatique
- Tests automatisés avec pytest

## Stack technique

| Rôle | Outil |
|---|---|
| Langage | Python 3.11+ |
| API | FastAPI + Uvicorn |
| Parser | Lark |
| Base de données | PostgreSQL 16 |
| ORM | SQLModel |
| Migrations | Alembic |
| Tests | pytest |

## Prérequis

- Python 3.11+
- Git
- Docker et Docker Compose (recommandé pour PostgreSQL)
  ou une installation locale de PostgreSQL 16

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/Mohamed00077/pseudocode-backend.git
cd pseudocode-backend

# 2. Environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\activate           # Windows

# 3. Dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env             # Windows : copy .env.example .env

# 5. Base de données
docker compose up -d
alembic upgrade head
```

## Lancer le serveur

```bash
uvicorn app.main:app --reload
```

- API : http://localhost:8000
- Documentation : http://localhost:8000/docs

## Tests

```bash
pytest
```

## Base de données et migrations

Après toute modification d'un modèle dans `app/models/` :

```bash
alembic revision --autogenerate -m "description du changement"
alembic upgrade head
```

Commitez le fichier de migration généré avec votre code.
Après un `git pull`, lancez `alembic upgrade head` pour être à jour.

## Structure du projet

```
app/
├── main.py          # point d'entrée FastAPI
├── config.py        # configuration (.env)
├── database.py      # connexion PostgreSQL
├── interpreter/     # grammaire et exécution du pseudo-code
├── models/          # modèles de base de données
└── routers/         # routes de l'API
migrations/          # migrations Alembic
tests/
```

## Contribuer

Le projet est développé en équipe.
Lisez [CONTRIBUTING.md](CONTRIBUTING.md) avant de commencer.

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
