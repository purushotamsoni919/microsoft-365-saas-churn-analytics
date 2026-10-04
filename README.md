# 🚀 Microsoft 365 SaaS Subscription & Customer Churn Analytics
**An End-to-End Enterprise Analytics Project built with Excel, SQL, Python, and Power BI**

---

## 📌 Executive Summary
This project analyzes a multi-tier SaaS customer portfolio modeled after **Microsoft 365 commercial subscriptions** across 5,000 enterprise and SMB accounts generating **$37.1M+ in Monthly Recurring Revenue (MRR)**.

The objective was to identify the primary telemetry drivers of customer churn, quantify the revenue impact of Copilot AI adoption, and deliver automated decision-support tools for executive leadership and account management teams.

---

## 🛠️ Technology Stack & Role Breakdown

```mermaid
flowchart TD
    A[Raw Telemetry & CRM Data<br/>5,000 Customer Accounts] --> B[1. SQL / T-SQL Engine<br/>Star Schema DDL, Window Functions,<br/>Cohort Retention & LTV Modeling]
    A --> C[2. Python Data Science<br/>Statistical Hypothesis Testing, EDA,<br/>Random Forest Churn Prediction (ROC-AUC 0.79)]
    B --> D[3. Power BI & DAX<br/>Star Schema Data Model,<br/>Time Intelligence & Churn Risk Heatmap]
    C --> E[4. Excel Executive Suite<br/>Dynamic KPI Model, XLOOKUP Tool,<br/>What-If Churn Sensitivity Model]
```

| Tool | Focus Area | Key Deliverables |
| :--- | :--- | :--- |
| **Microsoft Excel** | Financial & Scenario Modeling | Dynamic KPI model (`SUMIFS`, `COUNTIFS`), `XLOOKUP` Account Risk search engine, and a What-If Churn Reduction Sensitivity Model. |
| **SQL (MySQL / T-SQL / SQLite)** | Data Warehousing & Staging | Star Schema DDL, 30-Day Rolling Revenue Window queries, Top $N$ Dense Ranking per Industry, Churn Early Warning detector, and Customer Lifetime Value (LTV). Deployed directly into local MySQL Server (`m365_saas_analytics`). |
| **Python (Pandas / Scikit-Learn)** | Statistical Testing & ML | Chi-Square A/B test analysis ($\chi^2 = 74.28, p < 0.001$), Random Forest Churn Risk Classifier (ROC-AUC `0.7868`), and Automated MySQL ETL pipeline. |
| **Power BI / DAX** | Business Intelligence & Visuals | Star Schema Data Model, DAX Measures library (`CALCULATE`, `DIVIDE`, `SAMEPERIODLASTYEAR`), and Churn Early Warning Dashboard. |

---

## 🔑 Key Business Findings & Insights

1. **Copilot AI Adoption is the Strongest Retention Driver:**  
   Accounts with active Microsoft Copilot licenses experienced an average churn rate of **3.61%**, compared to **10.38%** for non-Copilot accounts—representing a **65.2% reduction in churn** ($\chi^2 = 74.28, p < 0.001$).
2. **Teams Engagement Threshold:**  
   Customer accounts where Teams active user percentage dropped below **35%** combined with **$\ge 3$ support tickets** had a **78% higher likelihood of churning** within 60 days.
3. **Revenue Preservation Opportunity:**  
   Our What-If Sensitivity Model proved that reducing overall churn by just **1.0%** preserves **$4.45M in annual ARR** across the current customer base.

---

## 📂 Project Repository Structure

```
Microsoft_Data_Analytics_Project/
├── 📁 01_Excel/
│   ├── Microsoft_365_SaaS_Analytics.xlsx   # Full interactive workbook (KPIs, XLOOKUP, What-If)
│   └── Excel_Walkthrough_Guide.md          # Guide to formulas, XLOOKUP, and sensitivity analysis
├── 📁 02_SQL/
│   ├── 01_schema_and_star_model.sql        # T-SQL Star Schema DDL (Facts, Dimensions & Indexes)
│   ├── 02_data_staging_and_load.sql        # T-SQL ETL data staging & population pipeline
│   ├── 03_advanced_analytics_queries.sql   # T-SQL Window functions, DENSE_RANK, LTV, Risk logic
│   ├── mysql_schema_and_queries.sql        # Complete MySQL 8.0 DDL & analytical queries
│   ├── sqlite_schema_and_queries.sql       # SQLite 3 DDL & queries for immediate practice
│   └── SQL_Interview_Walkthrough.md        # Dimensional modeling & technical interview guide
├── 📁 03_Python/
│   ├── 01_generate_saas_dataset.py         # Telemetry & customer data generation engine
│   ├── 02_eda_and_statistical_testing.py   # Statistical tests & hypothesis validation
│   ├── 03_churn_prediction_model.py        # Random Forest model & risk scoring
│   ├── load_data_to_mysql.py               # Automated MySQL database creator & data loader
│   └── charts/                             # High-res diagnostic visuals
├── 📁 04_PowerBI/
│   ├── Microsoft_365_Executive_Dashboard.html # Modern Interactive Executive Web Dashboard
│   ├── Microsoft_365_Modern_Theme.json        # Custom Soft-Blue Power BI Theme
│   ├── Microsoft_365_Excel_Connection.pbids   # 1-Click Power BI Data Source Connection
│   ├── PowerBI_Dashboard_Design_Guide.md      # Layout Coordinates & Visual Blueprint
│   ├── DAX_Measures.dax                       # Complete DAX measures library
│   └── PowerBI_Dashboard_Specification.md     # Data model & visual specs
├── 📁 data/
│   ├── dim_customers.csv                   # Raw customer dataset (5,000 accounts)
│   ├── dim_customers_scored.csv            # ML scored dataset with risk tiers
│   ├── dim_plans.csv                       # Subscription plans reference dataset
│   └── m365_analytics.db                   # SQLite database (contains full Star Schema tables)
└── 📁 presentation/
    └── Project_Executive_Summary.pdf       # 2-Page Executive Presentation Summary
```

---

## 🎙️ How to Present This Project in Your Interview

### 1. The 60-Second Pitch
> *"I built an end-to-end SaaS subscription and churn analytics project modeled on Microsoft 365 commercial subscriptions across 5,000 customer accounts. I used T-SQL to architect a Star Schema and calculate rolling revenue metrics and customer lifetime values. In Python, I ran hypothesis testing showing that Copilot adoption drops churn by 65%, and trained a Random Forest model to score customer risk tiers. Finally, I built interactive reporting in Power BI using DAX and developed an Excel dynamic financial model with What-If sensitivity scenarios showing how a 1% churn reduction saves $4.45M in ARR."*

### 2. Deep Dive by Tool
* **If they ask about SQL:** Point to `03_advanced_analytics_queries.sql`—explain how you used `ROWS BETWEEN 29 PRECEDING AND CURRENT ROW` for rolling averages and `DENSE_RANK()` for top spending enterprise clients.
* **If they ask about Python:** Point to `03_churn_prediction_model.py`—explain your feature engineering, handling class imbalance, and why Teams adoption was the #1 predictive feature.
* **If they ask about Power BI:** Point to `DAX_Measures.dax`—explain why you used `CALCULATE` for filter context modification and why star schema minimizes VertiPaq memory overhead.
* **If they ask about Excel:** Open `Microsoft_365_SaaS_Analytics.xlsx`—showcase the dynamic `XLOOKUP` search card and the sensitivity analysis table.
