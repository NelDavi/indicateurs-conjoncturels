-- Schéma PostgreSQL v1 pour la Plateforme Gabonaise des Indicateurs Conjoncturels (PGIC)
-- Couvre : authentification/roles, référentiel des indicateurs, séries/observations,
-- imports, publications, audit et workflow de validation.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- =========================
-- Types énumérés (domaines)
-- =========================
CREATE TYPE frequency_code AS ENUM ('D', 'W', 'M', 'Q', 'S', 'A');
CREATE TYPE workflow_status AS ENUM ('BROUILLON', 'EN_VALIDATION', 'VALIDE', 'PUBLIE', 'ARCHIVE');
CREATE TYPE role_scope AS ENUM ('SYSTEM', 'INTERNAL', 'PUBLIC_API');
CREATE TYPE publication_type AS ENUM ('BULLETIN_MENSUEL', 'RAPPORT_TRIMESTRIEL', 'NOTE_ANALYSE', 'AUTRE');
CREATE TYPE import_status AS ENUM ('UPLOADED', 'VALIDATING', 'REJECTED', 'APPROVED', 'PROCESSED');

-- =========================
-- Tables de sécurité
-- =========================
CREATE TABLE roles (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    scope           role_scope NOT NULL DEFAULT 'INTERNAL',
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           CITEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id         BIGINT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by     BIGINT REFERENCES users(id) ON DELETE SET NULL,
    PRIMARY KEY (user_id, role_id)
);

-- =========================
-- Référentiels métier
-- =========================
CREATE TABLE categories (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT,
    parent_id       BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    display_order   INTEGER NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sectors (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Indicateurs et séries
-- =========================
CREATE TABLE indicators (
    id                  BIGSERIAL PRIMARY KEY,
    code                TEXT NOT NULL UNIQUE,
    name                TEXT NOT NULL,
    description         TEXT,
    frequency           frequency_code NOT NULL,
    unit                TEXT NOT NULL,
    base_year           INTEGER CHECK (base_year BETWEEN 1900 AND 2200),
    source              TEXT NOT NULL,
    methodology         TEXT,
    category_id         BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    sector_id           BIGINT REFERENCES sectors(id) ON DELETE SET NULL,
    workflow_state      workflow_status NOT NULL DEFAULT 'BROUILLON',
    current_version     INTEGER NOT NULL DEFAULT 1 CHECK (current_version >= 1),
    is_archived         BOOLEAN NOT NULL DEFAULT FALSE,
    published_at        TIMESTAMPTZ,
    created_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    updated_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE data_series (
    id                  BIGSERIAL PRIMARY KEY,
    indicator_id        BIGINT NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    code                TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,
    is_primary          BOOLEAN NOT NULL DEFAULT FALSE,
    seasonal_adjustment TEXT,
    calculation_formula TEXT,
    decimals            SMALLINT NOT NULL DEFAULT 2 CHECK (decimals BETWEEN 0 AND 8),
    start_date          DATE,
    end_date            DATE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    updated_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (indicator_id, code),
    CHECK (start_date IS NULL OR end_date IS NULL OR start_date <= end_date)
);

CREATE TABLE observations (
    id                  BIGSERIAL PRIMARY KEY,
    series_id           BIGINT NOT NULL REFERENCES data_series(id) ON DELETE CASCADE,
    period_date         DATE NOT NULL,
    value               NUMERIC(20,6) NOT NULL,
    revision_number     INTEGER NOT NULL DEFAULT 0 CHECK (revision_number >= 0),
    is_published        BOOLEAN NOT NULL DEFAULT FALSE,
    status              workflow_status NOT NULL DEFAULT 'BROUILLON',
    note                TEXT,
    source_file_name    TEXT,
    imported_at         TIMESTAMPTZ,
    validated_at        TIMESTAMPTZ,
    published_at        TIMESTAMPTZ,
    created_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    updated_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (series_id, period_date, revision_number)
);

-- Un seul enregistrement publié par période/série (révision la plus récente publiée)
CREATE UNIQUE INDEX uq_observations_published_one_per_period
ON observations (series_id, period_date)
WHERE is_published;

-- =========================
-- Pipeline d'import
-- =========================
CREATE TABLE imports (
    id                  BIGSERIAL PRIMARY KEY,
    indicator_id        BIGINT REFERENCES indicators(id) ON DELETE SET NULL,
    uploaded_by         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    file_name           TEXT NOT NULL,
    file_sha256         TEXT,
    row_count           INTEGER CHECK (row_count IS NULL OR row_count >= 0),
    error_count         INTEGER NOT NULL DEFAULT 0 CHECK (error_count >= 0),
    status              import_status NOT NULL DEFAULT 'UPLOADED',
    validation_report   JSONB,
    uploaded_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at        TIMESTAMPTZ
);

CREATE TABLE import_rows (
    id                  BIGSERIAL PRIMARY KEY,
    import_id           BIGINT NOT NULL REFERENCES imports(id) ON DELETE CASCADE,
    row_number          INTEGER NOT NULL CHECK (row_number > 0),
    raw_payload         JSONB NOT NULL,
    is_valid            BOOLEAN NOT NULL DEFAULT TRUE,
    error_messages      JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (import_id, row_number)
);

-- =========================
-- Publications et audit
-- =========================
CREATE TABLE publications (
    id                  BIGSERIAL PRIMARY KEY,
    type                publication_type NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT,
    period_start        DATE,
    period_end          DATE,
    published_at        TIMESTAMPTZ,
    generated_by        BIGINT REFERENCES users(id) ON DELETE SET NULL,
    file_path           TEXT,
    metadata            JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (period_start IS NULL OR period_end IS NULL OR period_start <= period_end)
);

CREATE TABLE publication_indicators (
    publication_id      BIGINT NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    indicator_id        BIGINT NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    PRIMARY KEY (publication_id, indicator_id)
);

CREATE TABLE audit_logs (
    id                  BIGSERIAL PRIMARY KEY,
    event_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_user_id       BIGINT REFERENCES users(id) ON DELETE SET NULL,
    entity_type         TEXT NOT NULL,
    entity_id           TEXT NOT NULL,
    action              TEXT NOT NULL,
    old_data            JSONB,
    new_data            JSONB,
    ip_address          INET,
    user_agent          TEXT,
    correlation_id      UUID DEFAULT gen_random_uuid()
);

-- =========================
-- Index de performance
-- =========================
CREATE INDEX idx_indicators_sector ON indicators(sector_id);
CREATE INDEX idx_indicators_category ON indicators(category_id);
CREATE INDEX idx_indicators_workflow ON indicators(workflow_state);

CREATE INDEX idx_series_indicator ON data_series(indicator_id);
CREATE INDEX idx_series_active ON data_series(is_active);

CREATE INDEX idx_observations_series_period ON observations(series_id, period_date DESC);
CREATE INDEX idx_observations_status ON observations(status);
CREATE INDEX idx_observations_published_at ON observations(published_at);

CREATE INDEX idx_imports_status_uploaded_at ON imports(status, uploaded_at DESC);
CREATE INDEX idx_import_rows_import_id_valid ON import_rows(import_id, is_valid);

CREATE INDEX idx_publications_type_published ON publications(type, published_at DESC);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id, event_at DESC);
CREATE INDEX idx_audit_actor_event_at ON audit_logs(actor_user_id, event_at DESC);

-- =========================
-- Trigger générique updated_at
-- =========================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_roles_updated_at
BEFORE UPDATE ON roles
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_categories_updated_at
BEFORE UPDATE ON categories
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_sectors_updated_at
BEFORE UPDATE ON sectors
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_indicators_updated_at
BEFORE UPDATE ON indicators
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_data_series_updated_at
BEFORE UPDATE ON data_series
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_observations_updated_at
BEFORE UPDATE ON observations
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_publications_updated_at
BEFORE UPDATE ON publications
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;
