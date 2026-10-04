-- ============================================================================
-- MICROSOFT 365 SaaS SUBSCRIPTION & CHURN ANALYTICS - STAR SCHEMA DDL
-- Database Dialect: Microsoft SQL Server (T-SQL) / Azure SQL Database / Synapse
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: CLEANUP / DROP TABLES (IN REVERSE FOREIGN KEY DEPENDENCY ORDER)
-- Child fact tables must be dropped before parent dimension tables to avoid
-- Msg 3726: "Could not drop object because it is referenced by a FOREIGN KEY"
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.fact_monthly_usage', 'U') IS NOT NULL DROP TABLE dbo.fact_monthly_usage;
IF OBJECT_ID('dbo.fact_subscriptions', 'U') IS NOT NULL DROP TABLE dbo.fact_subscriptions;
IF OBJECT_ID('dbo.dim_customers', 'U') IS NOT NULL DROP TABLE dbo.dim_customers;
IF OBJECT_ID('dbo.dim_plans', 'U') IS NOT NULL DROP TABLE dbo.dim_plans;
GO

-- ----------------------------------------------------------------------------
-- STEP 2: CREATE DIMENSION TABLES
-- ----------------------------------------------------------------------------

-- 1. DIMENSION: Subscription Plans
CREATE TABLE dbo.dim_plans (
    plan_id INT IDENTITY(1,1) PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL UNIQUE,
    tier VARCHAR(20) NOT NULL, -- SMB, Enterprise
    monthly_price DECIMAL(10,2) NOT NULL,
    storage_limit_gb INT NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 2. DIMENSION: Customers
CREATE TABLE dbo.dim_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    company_size VARCHAR(30) NOT NULL, -- SMB (1-50), Mid-Market (51-500), Enterprise (500+)
    industry VARCHAR(50) NOT NULL,
    region VARCHAR(30) NOT NULL,       -- North America, EMEA, APAC, LATAM
    account_channel VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    is_active_flag BIT DEFAULT 1
);
GO

-- ----------------------------------------------------------------------------
-- STEP 3: CREATE FACT TABLES
-- ----------------------------------------------------------------------------

-- 3. FACT TABLE: Subscriptions & Recurring Revenue
CREATE TABLE dbo.fact_subscriptions (
    subscription_id INT IDENTITY(1001,1) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    plan_id INT NOT NULL,
    license_count INT NOT NULL,
    discount_pct DECIMAL(5,2) DEFAULT 0.00,
    mrr_amount DECIMAL(12,2) NOT NULL,
    auto_renewal_flag BIT DEFAULT 1,
    copilot_addon_flag BIT DEFAULT 0,
    churn_status_flag BIT DEFAULT 0,
    churn_date DATE NULL,
    CONSTRAINT FK_fact_sub_customer FOREIGN KEY (customer_id) REFERENCES dbo.dim_customers(customer_id),
    CONSTRAINT FK_fact_sub_plan FOREIGN KEY (plan_id) REFERENCES dbo.dim_plans(plan_id)
);
GO

-- 4. FACT TABLE: Monthly Usage & Telemetry
CREATE TABLE dbo.fact_monthly_usage (
    usage_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    usage_year_month INT NOT NULL, -- e.g. 202607
    teams_active_pct DECIMAL(5,2) NOT NULL,
    onedrive_gb_used DECIMAL(10,2) NOT NULL,
    support_tickets_raised INT DEFAULT 0,
    CONSTRAINT FK_fact_usage_customer FOREIGN KEY (customer_id) REFERENCES dbo.dim_customers(customer_id)
);
GO

-- ----------------------------------------------------------------------------
-- STEP 4: CREATE NONCLUSTERED INDEXES FOR QUERY OPTIMIZATION
-- ----------------------------------------------------------------------------
CREATE NONCLUSTERED INDEX IX_fact_subscriptions_churn 
    ON dbo.fact_subscriptions(churn_status_flag) 
    INCLUDE (mrr_amount, customer_id, plan_id);
GO

CREATE NONCLUSTERED INDEX IX_dim_customers_industry 
    ON dbo.dim_customers(industry, region);
GO

CREATE NONCLUSTERED INDEX IX_fact_monthly_usage_customer 
    ON dbo.fact_monthly_usage(customer_id, usage_year_month);
GO
