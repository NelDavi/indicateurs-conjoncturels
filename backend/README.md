# Backend PGIC (FastAPI)

## Lancer en local
1. Créer un environnement Python puis installer :
   - `pip install -r requirements.txt`
2. Exporter l'URL DB si besoin :
   - `export DATABASE_URL=postgresql+psycopg://pgic:pgic@localhost:5432/pgic`
3. Démarrer l'API :
   - `uvicorn app.main:app --reload`

## Endpoints MVP exposés
- `GET /api/indicators`
- `GET /api/indicators/{id}`
- `GET /api/series`
- `GET /api/data?indicator_id=&start=&end=`

Notes :
- `GET /api/indicators` et `GET /api/series` supportent `limit` et `offset`.
- `GET /api/indicators/{id}` renvoie `404` si l'indicateur n'existe pas.
- `GET /api/indicators` supporte aussi les filtres `q`, `frequency`, `sector_id`, `published_only`.

## Migration baseline
- Alembic est configuré dans `backend/alembic`.
- La migration `0001_baseline` exécute le SQL de `docs/db/schema_v1.sql`.


## Tests
- Exécuter : `python -m unittest backend.tests.test_routes`
