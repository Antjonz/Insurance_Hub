-- InsuranceHub Database Schema
-- Multi-insurer integration platform for Dutch insurance market

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- INSURERS: Insurance companies connected to the platform
-- ============================================================
CREATE TABLE insurers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    code            VARCHAR(20) UNIQUE NOT NULL,       -- Short code e.g. 'ACH' for Achmea
    api_endpoint    VARCHAR(255),                       -- Mock API endpoint URL
    api_format      VARCHAR(10) DEFAULT 'json',         -- Response format: json, xml
    api_status      VARCHAR(20) DEFAULT 'active',       -- active, inactive, error
    last_sync       TIMESTAMP,
    contact_email   VARCHAR(100),
    contact_phone   VARCHAR(20),
    address         TEXT,
    kvk_number      VARCHAR(20),                        -- Dutch Chamber of Commerce number
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PRODUCTS: Insurance products offered by each insurer
-- ============================================================
CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    insurer_id      INTEGER NOT NULL REFERENCES insurers(id) ON DELETE CASCADE,
    product_code    VARCHAR(30) UNIQUE NOT NULL,        -- e.g. 'ACH-WOZ-001'
    name            VARCHAR(150) NOT NULL,
    product_type    VARCHAR(30) NOT NULL,               -- property, life, health, auto, liability, travel
    description     TEXT,
    base_premium    DECIMAL(10,2) NOT NULL,             -- Monthly base premium in EUR
    coverage_amount DECIMAL(12,2),                      -- Maximum coverage in EUR
    deductible      DECIMAL(10,2) DEFAULT 0,            -- Eigen risico
    rules_json      JSONB,                              -- Calculation rules and parameters
    min_age         INTEGER DEFAULT 18,
    max_age         INTEGER DEFAULT 75,
    status          VARCHAR(20) DEFAULT 'active',       -- active, discontinued, pending
    effective_date  DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_insurer ON products(insurer_id);
CREATE INDEX idx_products_type ON products(product_type);
CREATE INDEX idx_products_status ON products(status);

-- ============================================================
-- POLICIES: Customer policies (polissen)
-- ============================================================
CREATE TABLE policies (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    policy_number   VARCHAR(30) UNIQUE NOT NULL,        -- e.g. 'POL-2024-00001'
    customer_name   VARCHAR(100) NOT NULL,
    customer_email  VARCHAR(100),
    customer_phone  VARCHAR(20),
    customer_bsn    VARCHAR(9),                          -- Burgerservicenummer (anonymized in demo)
    date_of_birth   DATE,
    address         TEXT,
    postcode        VARCHAR(7),                          -- Dutch postcode format: 1234 AB
    start_date      DATE NOT NULL,
    end_date        DATE,
    premium_amount  DECIMAL(10,2) NOT NULL,              -- Actual monthly premium
    payment_freq    VARCHAR(20) DEFAULT 'monthly',       -- monthly, quarterly, yearly
    status          VARCHAR(20) DEFAULT 'active',        -- active, expired, cancelled, pending
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policies_product ON policies(product_id);
CREATE INDEX idx_policies_status ON policies(status);
CREATE INDEX idx_policies_customer ON policies(customer_name);

-- ============================================================
-- CLAIMS: Insurance claims (schademeldingen)
-- ============================================================
CREATE TABLE claims (
    id              SERIAL PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(id),
    claim_number    VARCHAR(30) UNIQUE NOT NULL,         -- e.g. 'CLM-2024-00001'
    claim_date      DATE NOT NULL,
    reported_date   DATE DEFAULT CURRENT_DATE,
    amount          DECIMAL(10,2),                       -- Claimed amount
    approved_amount DECIMAL(10,2),                       -- Approved payout
    status          VARCHAR(20) DEFAULT 'submitted',     -- submitted, under_review, approved, rejected, paid
    category        VARCHAR(50),                          -- fire, theft, water_damage, accident, etc.
    description     TEXT NOT NULL,
    assessor_notes  TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_claims_policy ON claims(policy_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_date ON claims(claim_date);

-- ============================================================
-- SYNC_LOGS: Track data synchronization with insurers
-- ============================================================
CREATE TABLE sync_logs (
    id                  SERIAL PRIMARY KEY,
    insurer_id          INTEGER NOT NULL REFERENCES insurers(id),
    sync_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_type           VARCHAR(20) DEFAULT 'full',      -- full, incremental, manual
    status              VARCHAR(20) NOT NULL,             -- success, partial, failed
    records_processed   INTEGER DEFAULT 0,
    records_created     INTEGER DEFAULT 0,
    records_updated     INTEGER DEFAULT 0,
    records_failed      INTEGER DEFAULT 0,
    errors              TEXT,
    duration_ms         INTEGER,                          -- Sync duration in milliseconds
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_logs_insurer ON sync_logs(insurer_id);
CREATE INDEX idx_sync_logs_time ON sync_logs(sync_time);

-- ============================================================
-- VIEWS: Useful reporting views
-- ============================================================

-- Monthly premium revenue by insurer
CREATE OR REPLACE VIEW v_monthly_premiums AS
SELECT
    i.name AS insurer_name,
    i.code AS insurer_code,
    DATE_TRUNC('month', p.start_date) AS month,
    COUNT(p.id) AS policy_count,
    SUM(p.premium_amount) AS total_monthly_premium,
    AVG(p.premium_amount) AS avg_premium
FROM policies p
JOIN products pr ON p.product_id = pr.id
JOIN insurers i ON pr.insurer_id = i.id
WHERE p.status = 'active'
GROUP BY i.name, i.code, DATE_TRUNC('month', p.start_date)
ORDER BY month DESC, total_monthly_premium DESC;

-- Claims analysis by insurer and product type
CREATE OR REPLACE VIEW v_claims_analysis AS
SELECT
    i.name AS insurer_name,
    pr.product_type,
    COUNT(c.id) AS total_claims,
    SUM(c.amount) AS total_claimed,
    SUM(c.approved_amount) AS total_approved,
    AVG(c.amount) AS avg_claim_amount,
    COUNT(CASE WHEN c.status = 'approved' THEN 1 END) AS approved_count,
    COUNT(CASE WHEN c.status = 'rejected' THEN 1 END) AS rejected_count,
    ROUND(
        COUNT(CASE WHEN c.status = 'approved' THEN 1 END)::DECIMAL /
        NULLIF(COUNT(c.id), 0) * 100, 1
    ) AS approval_rate
FROM claims c
JOIN policies p ON c.policy_id = p.id
JOIN products pr ON p.product_id = pr.id
JOIN insurers i ON pr.insurer_id = i.id
GROUP BY i.name, pr.product_type
ORDER BY total_claims DESC;

-- Product comparison across insurers
CREATE OR REPLACE VIEW v_product_comparison AS
SELECT
    pr.product_type,
    i.name AS insurer_name,
    pr.name AS product_name,
    pr.base_premium,
    pr.coverage_amount,
    pr.deductible,
    COUNT(p.id) AS policies_sold,
    pr.status
FROM products pr
JOIN insurers i ON pr.insurer_id = i.id
LEFT JOIN policies p ON pr.id = p.product_id
GROUP BY pr.product_type, i.name, pr.name, pr.base_premium,
         pr.coverage_amount, pr.deductible, pr.status
ORDER BY pr.product_type, pr.base_premium;

-- Sync status overview
CREATE OR REPLACE VIEW v_sync_status AS
SELECT
    i.id AS insurer_id,
    i.name AS insurer_name,
    i.api_status,
    i.last_sync,
    sl.status AS last_sync_status,
    sl.records_processed AS last_records_processed,
    sl.duration_ms AS last_duration_ms,
    sl.errors AS last_errors,
    COUNT(sl2.id) FILTER (WHERE sl2.sync_time > NOW() - INTERVAL '24 hours') AS syncs_last_24h,
    COUNT(sl2.id) FILTER (WHERE sl2.status = 'failed' AND sl2.sync_time > NOW() - INTERVAL '24 hours') AS failures_last_24h
FROM insurers i
LEFT JOIN LATERAL (
    SELECT * FROM sync_logs WHERE insurer_id = i.id ORDER BY sync_time DESC LIMIT 1
) sl ON true
LEFT JOIN sync_logs sl2 ON sl2.insurer_id = i.id
GROUP BY i.id, i.name, i.api_status, i.last_sync, sl.status,
         sl.records_processed, sl.duration_ms, sl.errors;
