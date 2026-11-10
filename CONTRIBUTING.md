# Guide de contribution (backend)

## Règles de base

- Ne jamais pousser directement sur `main`.
- Une branche par tâche, une Pull Request par branche.
- Au moins une relecture par un autre membre avant de fusionner.
- Ne jamais commiter de secrets (`.env`, mots de passe, clés).

## Workflow

```bash
git checkout main
git pull
git checkout -b feature/nom-court
# ... travail et commits ...
git push -u origin feature/nom-court
```

Ouvrez ensuite une Pull Request vers `main` sur GitHub.

## Nommage des branches

- `feature/...` : nouvelle fonctionnalité
- `fix/...` : correction de bug
- `docs/...` : documentation
- `test/...` : tests

## Messages de commit

Format : `type: description courte`

```
feat: ajout de l'instruction TANT QUE
fix: correction du calcul de la division entière
docs: mise à jour du README
test: tests de l'instruction SI
```

## Avant d'ouvrir une Pull Request

- [ ] `pytest` passe
- [ ] Les nouveaux comportements ont des tests
- [ ] Si un modèle a changé : migration Alembic ajoutée
- [ ] Le README est à jour si nécessaire

## Base de données

Chacun utilise sa propre base locale (via Docker). Les changements de
schéma passent uniquement par des migrations Alembic, jamais par
des modifications manuelles.
