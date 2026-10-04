# 📊 Excel Executive Financial & Scenario Model Guide
**Workbook:** `Microsoft_365_SaaS_Analytics.xlsx`

---

## 1. Overview of Sheets

### Sheet 1: `Executive_KPI_Dashboard`
* **Dynamic KPIs:** Total Customer Accounts (`5,000`), Total Monthly Recurring Revenue (MRR: `$37.1M+`), Average ARPU, and Portfolio Churn Rate.
* **Formulas Used:**
  * `SUMIFS(dim_customers!K:K, ...)` for segment revenue aggregation.
  * `COUNTIFS(dim_customers!R:R, 1)` for churn count calculations.
  * `AVERAGEIFS(...)` for ARPU and telemetry benchmarking.

### Sheet 2: `Account_Risk_Lookup`
* **Interactive Search Tool:** Allows account executives to input any `customer_id` (e.g. `MS-10004`) to immediately display:
  * Company Size & Industry
  * Subscription Plan & MRR
  * Telemetry Health (Teams adoption %, Storage usage, Support ticket volume)
  * Copilot Activation Status & Calculated Churn Risk Tier
* **Formulas Used:**
  * Modern dynamic array `XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found])`.
  * Nested conditional formatting to flag accounts with $<35\%$ Teams usage or $\ge 3$ support tickets in red.

### Sheet 3: `What_If_Sensitivity_Analysis`
* **Financial Scenario Modeling:** Simulates the financial revenue impact of reducing customer churn across increments of 0.25%, 0.50%, 1.00%, and 2.00%.
* **Finding:** A modest **1.0% reduction in churn** preserves over **$4.45M in annual ARR** across the customer base.
