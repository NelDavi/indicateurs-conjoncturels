# Notes de conception — Schéma PostgreSQL v1

## Principes retenus
- **Traçabilité complète** : version d'indicateur, révisions d'observations, audit métier transverse.
- **Séparation des responsabilités** : référentiel (`indicators`), séries (`data_series`), données (`observations`), pipeline (`imports`).
- **Workflow explicite** : statut harmonisé sur indicateurs et observations.
- **Performance** : index centrés sur les requêtes de consultation temporelle et filtre métier.

## Règles métier clés
1. Une série peut avoir plusieurs révisions pour une même date (`revision_number`).
2. Une seule observation publiée est autorisée par couple (`series_id`, `period_date`) via index partiel.
3. Les imports sont historisés avec lignes détaillées pour diagnostic d'erreurs.
4. Les publications PDF sont liées explicitement aux indicateurs inclus.

## Prochaines étapes (implémentation)
1. Générer la migration Alembic baseline à partir de `schema_v1.sql`.
2. Créer les modèles SQLAlchemy alignés sur les contraintes SQL.
3. Exposer les endpoints FastAPI minimum :
   - `GET /api/indicators`
   - `GET /api/indicators/{id}`
   - `GET /api/series`
   - `GET /api/data?indicator_id=&start=&end=`
4. Ajouter les tests d'intégrité : clés, unicité, workflow, règles de publication.
