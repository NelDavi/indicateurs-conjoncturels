# Plan de démarrage recommandé

## Étape de départ proposée
**Commencer par l'étape 2 : conception du schéma PostgreSQL complet.**

Pourquoi commencer ici :
1. Le modèle de données est la fondation commune frontend/backend/API.
2. Il fixe les contrats métier (indicateur, série, observation, révision, audit).
3. Il permet de dériver rapidement :
   - les modèles SQLAlchemy,
   - les schémas Pydantic,
   - les endpoints FastAPI,
   - les écrans prioritaires du MVP.

## Sprint 0 (1 semaine)
1. Définir le dictionnaire des données (types, unités, fréquences, règles de validation).
2. Concevoir le schéma relationnel v1 (ERD + contraintes + index).
3. Initialiser les migrations Alembic.
4. Préparer des jeux de données de test (CSV exemples).

## Livrables
- Diagramme ERD v1.
- Scripts SQL initiaux + migration Alembic baseline.
- Spécification API minimale alignée avec le modèle.
- Documentation des conventions de nommage et versioning des observations.
