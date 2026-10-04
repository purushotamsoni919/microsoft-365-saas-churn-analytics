-- ============================================================================
-- MICROSOFT 365 SaaS ANALYTICS - MYSQL SCHEMA & ANALYTICAL QUERIES
-- Database Dialect: MySQL 8.0+ (InnoDB)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: CREATE DATABASE & SELECT SCHEMA
-- ----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS m365_saas_analytics;
USE m365_saas_analytics;

-- ----------------------------------------------------------------------------
-- STEP 2: DROP TABLES IN SAFE DEPENDENCY ORDER
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_monthly_usage;
DROP TABLE IF EXISTS fact_subscriptions;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_plans;

-- ----------------------------------------------------------------------------
-- STEP 3: DDL - STAR SCHEMA CREATION
-- ----------------------------------------------------------------------------

-- 1. DIMENSION: Subscription Plans
CREATE TABLE dim_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL UNIQUE,
    tier VARCHAR(20) NOT NULL,
    monthly_price DECIMAL(10,2) NOT NULL,
    storage_limit_gb INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. DIMENSION: Customers
CREATE TABLE dim_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    company_size VARCHAR(30) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    region VARCHAR(30) NOT NULL,
    account_channel VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    is_active_flag TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- 3. FACT TABLE: Subscriptions & Recurring Revenue
CREATE TABLE fact_subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    plan_id INT NOT NULL,
    license_count INT NOT NULL,
    discount_pct DECIMAL(5,2) DEFAULT 0.00,
    mrr_amount DECIMAL(12,2) NOT NULL,
    auto_renewal_flag TINYINT(1) DEFAULT 1,
    copilot_addon_flag TINYINT(1) DEFAULT 0,
    churn_status_flag TINYINT(1) DEFAULT 0,
    churn_date DATE NULL,
    CONSTRAINT fk_fact_sub_cust FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    CONSTRAINT fk_fact_sub_plan FOREIGN KEY (plan_id) REFERENCES dim_plans(plan_id)
) ENGINE=InnoDB;

-- 4. FACT TABLE: Monthly Usage & Telemetry
CREATE TABLE fact_monthly_usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    usage_year_month INT NOT NULL,
    teams_active_pct DECIMAL(5,2) NOT NULL,
    onedrive_gb_used DECIMAL(10,2) NOT NULL,
    support_tickets_raised INT DEFAULT 0,
    CONSTRAINT fk_fact_usage_cust FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
) ENGINE=InnoDB;

-- Indexes for Query Optimization
CREATE INDEX idx_fact_sub_churn ON fact_subscriptions(churn_status_flag, mrr_amount, customer_id);
CREATE INDEX idx_dim_cust_ind ON dim_customers(industry, region);
CREATE INDEX idx_fact_usage_cust ON fact_monthly_usage(customer_id, usage_year_month);

-- ----------------------------------------------------------------------------
-- STEP 4: SEED INITIAL PLANS
-- ----------------------------------------------------------------------------
INSERT INTO dim_plans (plan_id, plan_name, tier, monthly_price, storage_limit_gb) VALUES
(1, 'M365 Business Basic', 'SMB', 6.00, 1000),
(2, 'M365 Business Standard', 'SMB', 12.50, 1000),
(3, 'M365 Business Premium', 'SMB', 22.00, 1000),
(4, 'M365 E3', 'Enterprise', 36.00, 5000),
(5, 'M365 E5', 'Enterprise', 57.00, 5000);

-- ----------------------------------------------------------------------------
-- STEP 5: ANALYTICAL QUERIES (MYSQL 8.0+)
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
        AVG(s.churn_status_flag) AS churn_rate
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
    ROUND(AVG(s.churn_status_flag) * 100.0, 2) AS churn_rate_pct,
    SUM(CASE WHEN s.churn_status_flag = 1 THEN s.mrr_amount ELSE 0 END) AS lost_monthly_mrr
FROM dim_customers c
INNER JOIN fact_subscriptions s 
    ON c.customer_id = s.customer_id
GROUP BY s.copilot_addon_flag;
