# Product Requirements Document (PRD)

## Plateforme Gabonaise des Indicateurs Conjoncturels (PGIC)

Ce document formalise la vision, le périmètre fonctionnel et les choix techniques de la plateforme nationale de suivi et de production des indicateurs conjoncturels du Gabon.

## Objectifs
- Centraliser les indicateurs macroéconomiques et sectoriels.
- Permettre la visualisation dynamique et l'export des séries.
- Automatiser la production à partir de données brutes.
- Garantir traçabilité, historisation des révisions et auditabilité.
- Exposer une API Open Data standardisée.

## Cibles
- **Public** : chercheurs, étudiants, journalistes, institutions internationales, citoyens.
- **Interne** : analystes statistiques, économistes, administrateurs, producteurs de données.

## Architecture cible
- **Frontend** : React + TypeScript + Vite, TailwindCSS, DaisyUI, Recharts/ECharts.
- **Backend** : FastAPI (prioritaire), SQLAlchemy, Alembic.
- **Base de données** : PostgreSQL.
- **Ops** : Docker, Docker Compose, Nginx, CI/CD GitHub Actions.

## Fonctionnalités clés
### Portail public
- Accueil avec indicateurs clés, publications récentes, filtres rapides.
- Fiche indicateur : métadonnées, historique, graphique interactif, export CSV/Excel, endpoint API.
- Recherche multicritère : mot-clé, secteur, fréquence, auto-complétion.
- API Open Data :
  - `/api/indicators`
  - `/api/indicators/{id}`
  - `/api/series`
  - `/api/data?indicator_id=&start=&end=`

### Espace administrateur
- Authentification JWT + rôles (Super Admin, Analyste, Éditeur, Lecteur interne).
- CRUD indicateurs, archivage, versioning.
- Import CSV/Excel avec validation et prévisualisation.
- Moteur de calcul (moyennes mobiles, base 100, variations, indices chaînés).
- Workflow de validation (Brouillon → En validation → Validé → Publié).
- Génération de publications PDF (bulletin mensuel, rapport trimestriel).

## Modèle de données (noyau)
Tables de base : `users`, `roles`, `indicators`, `categories`, `sectors`, `data_series`, `observations`, `imports`, `publications`, `audit_logs`.

Exemple d'attributs indicateur :
- `id`, `code`, `name`, `description`, `frequency`, `unit`, `base_year`, `source`, `methodology`, `created_at`, `updated_at`.

Exemple d'attributs observation :
- `id`, `indicator_id`, `date`, `value`, `revision_number`, `is_published`.

## Non-fonctionnel
- Sécurité : bcrypt, CORS, rate limiting, validation stricte, logs sécurisés.
- Performance : indexation PostgreSQL, pagination, lazy loading, compression.
- Qualité : tests unitaires/intégration backend, composants/E2E frontend.
- Disponibilité cible : 99% uptime.

## Roadmap
- **Phase 1 (MVP)** : auth, CRUD indicateurs, import CSV, graphiques, API publique.
- **Phase 2** : workflow, PDF, versioning, audit logs.
- **Phase 3** : correction saisonnière, Redis, monitoring, analytics.
