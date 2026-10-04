-- ============================================================================
-- MICROSOFT 365 SaaS SUBSCRIPTION & CHURN ANALYTICS - DATA INGESTION & ETL
-- Database Dialect: Microsoft SQL Server (T-SQL) / Azure SQL Database
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: POPULATE DIMENSION: dim_plans
-- ----------------------------------------------------------------------------
SET IDENTITY_INSERT dbo.dim_plans ON;

INSERT INTO dbo.dim_plans (plan_id, plan_name, tier, monthly_price, storage_limit_gb, created_at)
VALUES 
    (1, 'M365 Business Basic', 'SMB', 6.00, 1000, '2024-01-01'),
    (2, 'M365 Business Standard', 'SMB', 12.50, 1000, '2024-01-01'),
    (3, 'M365 Business Premium', 'SMB', 22.00, 1000, '2024-01-01'),
    (4, 'M365 E3', 'Enterprise', 36.00, 5000, '2024-01-01'),
    (5, 'M365 E5', 'Enterprise', 57.00, 5000, '2024-01-01');

SET IDENTITY_INSERT dbo.dim_plans OFF;
GO

-- ----------------------------------------------------------------------------
-- STEP 2: CREATE STAGING TABLE FOR RAW CSV INGESTION
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.stg_customers_raw', 'U') IS NOT NULL DROP TABLE dbo.stg_customers_raw;
GO

CREATE TABLE dbo.stg_customers_raw (
    customer_id VARCHAR(20),
    company_size VARCHAR(30),
    industry VARCHAR(50),
    region VARCHAR(30),
    account_channel VARCHAR(50),
    signup_date DATE,
    plan_name VARCHAR(50),
    unit_price DECIMAL(10,2),
    license_count INT,
    discount_pct DECIMAL(5,2),
    mrr DECIMAL(12,2),
    tenure_months INT,
    teams_adoption_pct DECIMAL(5,2),
    onedrive_gb DECIMAL(10,2),
    support_tickets INT,
    copilot_enabled BIT,
    auto_renewal BIT,
    churned BIT
);
GO

-- ----------------------------------------------------------------------------
-- STEP 3: OPTION A - BULK INSERT FROM CSV (IF RUNNING LOCALLY ON SQL SERVER)
-- Note: Update path to match your environment if running via SSMS/sqlcmd:
--
-- BULK INSERT dbo.stg_customers_raw
-- FROM 'D:\New folder\PK\DATA ANALYST\Microsoft_Data_Analytics_Project\data\dim_customers.csv'
-- WITH (
--     FORMAT = 'CSV',
--     FIRSTROW = 2,
--     FIELDTERMINATOR = ',',
--     ROWTERMINATOR = '\n',
--     TABLOCK
-- );
-- GO
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- STEP 4: TRANSFORM & LOAD INTO STAR SCHEMA
-- ----------------------------------------------------------------------------

-- 4.1 Ingest into dbo.dim_customers
INSERT INTO dbo.dim_customers (customer_id, company_size, industry, region, account_channel, signup_date, is_active_flag)
SELECT 
    s.customer_id,
    s.company_size,
    s.industry,
    s.region,
    s.account_channel,
    s.signup_date,
    CASE WHEN s.churned = 1 THEN 0 ELSE 1 END AS is_active_flag
FROM dbo.stg_customers_raw s
WHERE NOT EXISTS (SELECT 1 FROM dbo.dim_customers c WHERE c.customer_id = s.customer_id);
GO

-- 4.2 Ingest into dbo.fact_subscriptions
INSERT INTO dbo.fact_subscriptions (
    customer_id, plan_id, license_count, discount_pct, mrr_amount, 
    auto_renewal_flag, copilot_addon_flag, churn_status_flag, churn_date
)
SELECT 
    s.customer_id,
    p.plan_id,
    s.license_count,
    s.discount_pct,
    s.mrr,
    s.auto_renewal,
    s.copilot_enabled,
    s.churned,
    CASE WHEN s.churned = 1 THEN DATEADD(day, -30, '2026-08-01') ELSE NULL END AS churn_date
FROM dbo.stg_customers_raw s
INNER JOIN dbo.dim_plans p 
    ON s.plan_name = p.plan_name;
GO

-- 4.3 Ingest into dbo.fact_monthly_usage
INSERT INTO dbo.fact_monthly_usage (
    customer_id, usage_year_month, teams_active_pct, onedrive_gb_used, support_tickets_raised
)
SELECT 
    s.customer_id,
    202607 AS usage_year_month,
    s.teams_adoption_pct,
    s.onedrive_gb,
    s.support_tickets
FROM dbo.stg_customers_raw s;
GO

-- ----------------------------------------------------------------------------
-- STEP 5: VERIFY ROW COUNTS & DATA INTEGRITY
-- ----------------------------------------------------------------------------
SELECT 'dim_plans' AS table_name, COUNT(*) AS total_rows FROM dbo.dim_plans
UNION ALL
SELECT 'dim_customers', COUNT(*) FROM dbo.dim_customers
UNION ALL
SELECT 'fact_subscriptions', COUNT(*) FROM dbo.fact_subscriptions
UNION ALL
SELECT 'fact_monthly_usage', COUNT(*) FROM dbo.fact_monthly_usage;
GO
