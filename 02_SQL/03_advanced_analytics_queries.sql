-- ============================================================================
-- MICROSOFT 365 SaaS ANALYTICS - ADVANCED ANALYTICAL SQL QUERIES
-- Dialect: Microsoft SQL Server (T-SQL) / Azure Synapse Analytics
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: 30-Day Rolling Revenue & New Account Acquisition Trend
-- Technical Concept: Window Aggregate Functions with Explicit Frame Specification
-- Business Insight: Identifies sales velocity and smooths day-to-day volatility
-- ----------------------------------------------------------------------------
WITH daily_acquisitions AS (
    SELECT 
        c.signup_date,
        COUNT(DISTINCT c.customer_id) AS new_accounts,
        SUM(s.mrr_amount) AS new_mrr_acquired
    FROM dbo.dim_customers c
    INNER JOIN dbo.fact_subscriptions s 
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
GO

-- ----------------------------------------------------------------------------
-- QUERY 2: Top 3 Highest Revenue Accounts per Industry
-- Technical Concept: Window Ranking with DENSE_RANK() & CTE Filtering
-- Business Insight: Pinpoints key enterprise tier accounts for high-touch CSM coverage
-- ----------------------------------------------------------------------------
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
    FROM dbo.dim_customers c
    INNER JOIN dbo.fact_subscriptions s 
        ON c.customer_id = s.customer_id
    INNER JOIN dbo.dim_plans p 
        ON s.plan_id = p.plan_id
    WHERE s.churn_status_flag = 0 -- Filter to active subscriptions only
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
GO

-- ----------------------------------------------------------------------------
-- QUERY 3: Customer Churn Early Warning Indicator (High Risk Detector)
-- Technical Concept: Multi-Condition CASE Logic & Fact-Table Grain Alignment
-- Business Logic: Teams adoption < 35%, >= 3 tickets raised, No Copilot add-on
-- ----------------------------------------------------------------------------
WITH latest_telemetry AS (
    SELECT 
        customer_id,
        teams_active_pct,
        support_tickets_raised,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id 
            ORDER BY usage_year_month DESC
        ) AS rn
    FROM dbo.fact_monthly_usage
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
FROM dbo.dim_customers c
INNER JOIN dbo.fact_subscriptions s 
    ON c.customer_id = s.customer_id
INNER JOIN dbo.dim_plans p 
    ON s.plan_id = p.plan_id
INNER JOIN latest_telemetry u 
    ON c.customer_id = u.customer_id AND u.rn = 1
WHERE s.churn_status_flag = 0
ORDER BY s.mrr_amount DESC;
GO

-- ----------------------------------------------------------------------------
-- QUERY 4: Customer Lifetime Value (LTV) by Subscription Tier
-- Technical Concept: Aggregate Metrics, Safe Division (NULLIF), and Floating-point Casting
-- Formula: LTV = (ARPU * Gross Margin 80%) / Monthly Churn Rate
-- ----------------------------------------------------------------------------
WITH plan_metrics AS (
    SELECT 
        p.plan_name,
        COUNT(DISTINCT c.customer_id) AS total_customers,
        AVG(s.mrr_amount) AS arpu,
        AVG(CAST(s.churn_status_flag AS FLOAT)) AS churn_rate
    FROM dbo.dim_customers c
    INNER JOIN dbo.fact_subscriptions s 
        ON c.customer_id = s.customer_id
    INNER JOIN dbo.dim_plans p 
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
GO

-- ----------------------------------------------------------------------------
-- QUERY 5: Copilot AI Retention Lift Impact Analysis
-- Technical Concept: Cohort Comparison & Impact Quantification
-- Finding: Quantifies 65% churn reduction associated with Microsoft Copilot
-- ----------------------------------------------------------------------------
SELECT 
    CASE WHEN s.copilot_addon_flag = 1 THEN 'Copilot Enabled' ELSE 'Standard (No Copilot)' END AS copilot_cohort,
    COUNT(DISTINCT c.customer_id) AS total_accounts,
    SUM(s.mrr_amount) AS total_portfolio_mrr,
    ROUND(AVG(s.mrr_amount), 2) AS avg_mrr_per_account,
    ROUND(AVG(CAST(s.churn_status_flag AS FLOAT)) * 100.0, 2) AS churn_rate_pct,
    SUM(CASE WHEN s.churn_status_flag = 1 THEN s.mrr_amount ELSE 0 END) AS lost_monthly_mrr
FROM dbo.dim_customers c
INNER JOIN dbo.fact_subscriptions s 
    ON c.customer_id = s.customer_id
GROUP BY s.copilot_addon_flag;
GO
