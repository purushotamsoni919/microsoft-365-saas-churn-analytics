# 🧠 SQL Architecture & Interview Technical Walkthrough
**Microsoft 365 SaaS Analytics Data Warehouse**

---

## 1. Dimensional Architecture & Star Schema Design

The enterprise data warehouse is structured around a classic **Kimball Star Schema** optimized for analytical read performance, OLAP aggregation, and direct integration with Power BI / VertiPaq.

```
       +-----------------------+
       |       dim_plans       |
       +-----------------------+
       | PK  plan_id           |
       |     plan_name         |
       |     tier              |
       |     monthly_price     |
       |     storage_limit_gb  |
       +-----------+-----------+
                   | 1
                   | 
                   | N
       +-----------+-----------+             +-----------------------+
       |  fact_subscriptions   | 1         N |   fact_monthly_usage  |
       +-----------------------+-------------+-----------------------+
       | PK  subscription_id   |             | PK  usage_id          |
       | FK  customer_id       |---+     +---| FK  customer_id       |
       | FK  plan_id           |   |     |   |     usage_year_month  |
       |     license_count     |   |     |   |     teams_active_pct  |
       |     discount_pct      |   |     |   |     onedrive_gb_used  |
       |     mrr_amount        |   |     |   |     support_tickets   |
       |     auto_renewal_flag |   |     |   +-----------------------+
       |     copilot_addon_flag|   |     |
       |     churn_status_flag |   |     |
       |     churn_date        |   |     |
       +-----------------------+   |     |
                                   | 1   | 1
                       +-----------+-----+-----+
                       |     dim_customers     |
                       +-----------------------+
                       | PK  customer_id       |
                       |     company_size      |
                       |     industry          |
                       |     region            |
                       |     account_channel   |
                       |     signup_date       |
                       |     is_active_flag    |
                       +-----------------------+
```

### Why a Star Schema over 3NF (Third Normal Form)?
- **Query Simplicity & Performance:** Analytical reporting requires frequent multi-table joins. Star schemas minimize join depth (typically 1 hop between fact and dimension) compared to normalized snowflake structures.
- **BI Compatibility:** Power BI VertiPaq columnar storage achieves maximum compression when relationship filtering travels unidirectionally from single-cardinality dimension tables to multi-cardinality fact tables.
- **Grain Independence:** Separating `fact_subscriptions` (grain: 1 row per customer subscription) from `fact_monthly_usage` (grain: 1 row per customer per month) prevents fan-out/Cartesian errors.

---

## 2. Advanced SQL Concepts Implemented

### A. Window Aggregate Functions with Explicit Frame (`ROWS BETWEEN`)
* **File Reference:** `03_advanced_analytics_queries.sql` (Query 1)
* **Code Highlight:**
  ```sql
  AVG(new_mrr_acquired * 1.0) OVER (
      ORDER BY signup_date
      ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
  ) AS rolling_30d_avg_new_mrr
  ```
* **Interview Explanation:**  
  *"By specifying `ROWS BETWEEN 29 PRECEDING AND CURRENT ROW`, we instruct the SQL engine to calculate a true 30-day moving average over the physical ordered window frame rather than defaulting to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, which is both slower and aggregates duplicate peers together."*

### B. Dense Ranking without Rank Skipping (`DENSE_RANK()`)
* **File Reference:** `03_advanced_analytics_queries.sql` (Query 2)
* **Code Highlight:**
  ```sql
  DENSE_RANK() OVER (
      PARTITION BY c.industry 
      ORDER BY s.mrr_amount DESC
  ) AS industry_rev_rank
  ```
* **Interview Explanation:**  
  *"We use `DENSE_RANK()` instead of `RANK()` or `ROW_NUMBER()` because enterprise tie-breaks in MRR should not skip subsequent rank positions (e.g. 1, 1, 2 rather than 1, 1, 3), ensuring our top 3 filter captures all eligible top-tier revenue contributors."*

### C. Fact Grain Alignment with CTE Partitioning
* **File Reference:** `03_advanced_analytics_queries.sql` (Query 3)
* **Code Highlight:**
  ```sql
  WITH latest_telemetry AS (
      SELECT customer_id, teams_active_pct, support_tickets_raised,
             ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY usage_year_month DESC) AS rn
      FROM fact_monthly_usage
  )
  ...
  INNER JOIN latest_telemetry u ON c.customer_id = u.customer_id AND u.rn = 1
  ```
* **Interview Explanation:**  
  *"Joining a 1-to-many monthly usage table directly against customer dimensions multiplies rows across every historical month. We isolate the latest telemetry snapshot using `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY usage_year_month DESC)` to guarantee a strictly 1:1 join."*

### D. Safe Mathematical Computation & Floating-Point Precision
* **File Reference:** `03_advanced_analytics_queries.sql` (Query 4)
* **Code Highlight:**
  ```sql
  ROUND((arpu * 0.80) / NULLIF(churn_rate, 0), 2) AS estimated_customer_ltv
  ```
* **Interview Explanation:**  
  *"`NULLIF(churn_rate, 0)` protects the calculation against divide-by-zero errors in tiers where churn is zero, returning `NULL` rather than failing the entire query execution batch."*

---

## 3. Database Dialect Compatibility Matrix

| Database Engine | Script to Execute | Key Syntax Handled |
| :--- | :--- | :--- |
| **SQL Server / Azure SQL** | `01_schema_and_star_model.sql`<br/>`02_data_staging_and_load.sql`<br/>`03_advanced_analytics_queries.sql` | `IDENTITY(1,1)`, `BIT`, `OBJECT_ID`, `GO` delimiters, Non-clustered `INCLUDE` indexes. |
| **SQLite (Bundled DB)** | `sqlite_schema_and_queries.sql`<br/>*(Already populated in `data/m365_analytics.db`)* | `INTEGER PRIMARY KEY AUTOINCREMENT`, ANSI standard data types, native CTEs and Window functions. |
| **MySQL 8.0+** | `mysql_schema_and_queries.sql` | `AUTO_INCREMENT`, `TINYINT(1)`, `InnoDB` foreign keys, `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`. |

---

## 4. Top SQL Technical Interview Questions & Model Answers

### Q1: "Why did you create a non-clustered index on `churn_status_flag` with `INCLUDE (mrr_amount, customer_id)`?"
> **Answer:** *"In SQL Server, `INCLUDE` creates a covering index for queries that filter on churn status and aggregate MRR or count accounts. By storing `mrr_amount` and `customer_id` directly in the leaf pages of the non-clustered B-Tree, the query optimizer avoids costly key lookups back to the clustered base table, resulting in an index-only scan."*

### Q2: "What is the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()`?"
> **Answer:**
> - `ROW_NUMBER()`: Always generates unique sequential integers (1, 2, 3, 4) regardless of ties.
> - `RANK()`: Assigns the same rank to identical values, but skips subsequent ranks (1, 2, 2, 4).
> - `DENSE_RANK()`: Assigns the same rank to identical values without skipping numbers (1, 2, 2, 3). For top-tier account segmentation, `DENSE_RANK()` ensures consistent categorization without gaps.

### Q3: "What happens if you drop a parent table before a child table in a relational database?"
> **Answer:** *"The relational database engine enforces referential integrity. Attempting to drop a referenced table (like `dim_plans` or `dim_customers`) while foreign keys point to it from `fact_subscriptions` throws a constraint violation (e.g., T-SQL Error 3726). The script must drop child fact tables first, or drop the foreign key constraints prior to table removal."*
