-- ============================================================================
-- MICROSOFT 365 SaaS ANALYTICS - SQLITE SCHEMA & ANALYTICAL QUERIES
-- Database Dialect: SQLite 3 (Fully compatible with data/m365_analytics.db)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- SECTION 1: STAR SCHEMA DDL
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_monthly_usage;
DROP TABLE IF EXISTS fact_subscriptions;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_plans;

-- 1. DIMENSION: Subscription Plans
CREATE TABLE dim_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL,
    monthly_price REAL NOT NULL,
    storage_limit_gb INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 2. DIMENSION: Customers
CREATE TABLE dim_customers (
    customer_id TEXT PRIMARY KEY,
    company_size TEXT NOT NULL,
    industry TEXT NOT NULL,
    region TEXT NOT NULL,
    account_channel TEXT NOT NULL,
    signup_date TEXT NOT NULL,
    is_active_flag INTEGER DEFAULT 1
);

-- 3. FACT TABLE: Subscriptions & Recurring Revenue
CREATE TABLE fact_subscriptions (
    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    plan_id INTEGER NOT NULL,
    license_count INTEGER NOT NULL,
    discount_pct REAL DEFAULT 0.00,
    mrr_amount REAL NOT NULL,
    auto_renewal_flag INTEGER DEFAULT 1,
    copilot_addon_flag INTEGER DEFAULT 0,
    churn_status_flag INTEGER DEFAULT 0,
    churn_date TEXT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (plan_id) REFERENCES dim_plans(plan_id)
);

-- 4. FACT TABLE: Monthly Usage & Telemetry
CREATE TABLE fact_monthly_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    usage_year_month INTEGER NOT NULL,
    teams_active_pct REAL NOT NULL,
    onedrive_gb_used REAL NOT NULL,
    support_tickets_raised INTEGER DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
);

-- Indexes for Query Acceleration
CREATE INDEX idx_fact_subscriptions_churn ON fact_subscriptions(churn_status_flag, mrr_amount, customer_id);
CREATE INDEX idx_dim_customers_industry ON dim_customers(industry, region);
CREATE INDEX idx_fact_usage_customer ON fact_monthly_usage(customer_id, usage_year_month);

-- ----------------------------------------------------------------------------
-- SECTION 2: ADVANCED ANALYTICAL QUERIES (RUN DIRECTLY ON SQLite)
-- ----------------------------------------------------------------------------

-- QUERY 1: 30-Day Rolling Revenue & New Account Acquisition Trend
WITH daily_acquisitions AS (
    SELECT 
        c.signup_date,
        COUNT(DISTINCT c.customer_id) AS new_accounts,
        SUM(s.mrr_amount) AS new_mrr_acquired
    FROM dim_customers c
    INNER JOIN fact_subscriptions s 
        ON c.customer_id = s.customer_id
    GROUP BY c.signup_date
)
SELECT 
    signup_date,
    new_accounts,
    new_mrr_acquired,
    ROUND(
        AVG(new_mrr_acquired * 1.0) OVER (
            ORDER BY signup_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ), 2
    ) AS rolling_30d_avg_new_mrr
FROM daily_acquisitions
ORDER BY signup_date DESC;

-- QUERY 2: Top 3 Highest Revenue Accounts per Industry (Dense Ranking)
WITH ranked_enterprise_accounts AS (
    SELECT 
        c.industry,
        c.customer_id,
        c.region,
        p.plan_name,
        s.license_count,
        s.mrr_amount,
        DENSE_RANK() OVER (
            PARTITION BY c.industry 
            ORDER BY s.mrr_amount DESC
        ) AS industry_rev_rank
    FROM dim_customers c
    INNER JOIN fact_subscriptions s 
        ON c.customer_id = s.customer_id
    INNER JOIN dim_plans p 
        ON s.plan_id = p.plan_id
    WHERE s.churn_status_flag = 0
)
SELECT 
    industry,
    industry_rev_rank,
    customer_id,
    region,
    plan_name,
    license_count,
    mrr_amount
FROM ranked_enterprise_accounts
WHERE industry_rev_rank <= 3
ORDER BY industry, industry_rev_rank;

-- QUERY 3: Customer Churn Early Warning Indicator (High Risk Detector)
WITH latest_telemetry AS (
    SELECT 
        customer_id,
        teams_active_pct,
        support_tickets_raised,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id 
            ORDER BY usage_year_month DESC
        ) AS rn
    FROM fact_monthly_usage
)
SELECT 
    c.customer_id,
    c.industry,
    c.region,
    p.plan_name,
    s.mrr_amount,
    u.teams_active_pct,
    u.support_tickets_raised,
    s.copilot_addon_flag,
    CASE 
        WHEN u.teams_active_pct < 35.0 AND u.support_tickets_raised >= 3 AND s.copilot_addon_flag = 0 
            THEN 'CRITICAL - HIGH CHURN RISK'
        WHEN u.teams_active_pct < 50.0 OR u.support_tickets_raised >= 3 
            THEN 'WARNING - MEDIUM RISK'
        ELSE 'HEALTHY'
    END AS account_health_status
FROM dim_customers c
INNER JOIN fact_subscriptions s 
    ON c.customer_id = s.customer_id
INNER JOIN dim_plans p 
    ON s.plan_id = p.plan_id
INNER JOIN latest_telemetry u 
    ON c.customer_id = u.customer_id AND u.rn = 1
WHERE s.churn_status_flag = 0
ORDER BY s.mrr_amount DESC;

-- QUERY 4: Customer Lifetime Value (LTV) by Subscription Tier
WITH plan_metrics AS (
    SELECT 
        p.plan_name,
        COUNT(DISTINCT c.customer_id) AS total_customers,
        AVG(s.mrr_amount) AS arpu,
        AVG(CAST(s.churn_status_flag AS REAL)) AS churn_rate
    FROM dim_customers c
    INNER JOIN fact_subscriptions s 
        ON c.customer_id = s.customer_id
    INNER JOIN dim_plans p 
        ON s.plan_id = p.plan_id
    GROUP BY p.plan_name
)
SELECT 
    plan_name,
    total_customers,
    ROUND(arpu, 2) AS avg_arpu,
    ROUND(churn_rate * 100, 2) AS churn_rate_pct,
    ROUND((arpu * 0.80) / NULLIF(churn_rate, 0), 2) AS estimated_customer_ltv
FROM plan_metrics
ORDER BY estimated_customer_ltv DESC;

-- QUERY 5: Copilot AI Retention Lift Impact Analysis
SELECT 
    CASE WHEN s.copilot_addon_flag = 1 THEN 'Copilot Enabled' ELSE 'Standard (No Copilot)' END AS copilot_cohort,
    COUNT(DISTINCT c.customer_id) AS total_accounts,
    SUM(s.mrr_amount) AS total_portfolio_mrr,
    ROUND(AVG(s.mrr_amount), 2) AS avg_mrr_per_account,
    ROUND(AVG(CAST(s.churn_status_flag AS REAL)) * 100.0, 2) AS churn_rate_pct,
    SUM(CASE WHEN s.churn_status_flag = 1 THEN s.mrr_amount ELSE 0 END) AS lost_monthly_mrr
FROM dim_customers c
INNER JOIN fact_subscriptions s 
    ON c.customer_id = s.customer_id
GROUP BY s.copilot_addon_flag;
