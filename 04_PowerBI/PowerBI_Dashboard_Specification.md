# 📊 Power BI Dashboard Specification & Interview Walkthrough

## 1. Data Model Architecture (Star Schema)
The Power BI model is architected following Microsoft best practices for the VertiPaq engine:
- **`Dim_Customers` (1)** $\longrightarrow$ **`Fact_Subscriptions` (\*)** (Single direction filter on `customer_id`)
- **`Dim_Plans` (1)** $\longrightarrow$ **`Fact_Subscriptions` (\*)** (Single direction filter on `plan_id`)
- **`Dim_Date` (1)** $\longrightarrow$ **`Fact_Subscriptions` (\*)** (Single direction filter on `signup_date`)
- **`Dim_Customers` (1)** $\longrightarrow$ **`Fact_Monthly_Usage` (\*)** (Single direction filter on `customer_id`)

---

## 2. Dashboard Pages Breakdown

### Page 1: Executive KPI & Revenue Health
* **Top KPI Cards:** Total ARR (`$445.8M`), Active Customer Accounts (`4,610`), Portfolio Churn Rate (`7.80%`), Average ARPU (`$7,430/mo`).
* **Visual 1 (Donut Chart):** ARR Breakdown by Subscription Plan (`M365 E5`, `M365 E3`, `Business Standard`, `Business Premium`).
* **Visual 2 (Clustered Bar Chart):** Active Revenue vs. Churned Revenue by Industry.
* **Visual 3 (Line & Clustered Column):** Monthly Signups vs. 30-Day Moving Average Revenue.

### Page 2: Product Adoption & Churn Early Warning System
* **Visual 1 (Scatter Plot):** Teams Adoption Rate (%) vs. Support Tickets vs. Churn Status (Red/Green points).
* **Visual 2 (Bar Chart):** Churn Rate by Copilot AI Activation (Shows a **65% lower churn rate** for accounts adopting Copilot).
* **Visual 3 (Table Matrix):** High-Risk Customer Alert Table displaying accounts with $<35\%$ Teams usage and $\ge 3$ support tickets.

---

## 3. Key Interview Talking Points for Power BI
1. *"I used measures instead of calculated columns for all aggregations and ratios to conserve RAM in the VertiPaq engine."*
2. *"I implemented dynamic formatting and DAX error handling using `DIVIDE(..., ..., 0)` to prevent divide-by-zero exceptions."*
3. *"The data model uses a clean 1-to-many Star Schema, avoiding bi-directional filters to ensure fast query rendering."*
