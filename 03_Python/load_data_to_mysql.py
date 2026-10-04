"""
Automated ETL pipeline to create and populate the Star Schema in MySQL.
Database: m365_saas_analytics
"""

import os
import pandas as pd
import mysql.connector

# Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "Root@12345"
DB_NAME = "m365_saas_analytics"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def setup_and_load_mysql():
    print(f"Connecting to MySQL server at {DB_HOST}...")
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()

    print(f"Creating database `{DB_NAME}` if not exists...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
    cursor.execute(f"USE {DB_NAME};")

    print("Recreating Star Schema tables...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("DROP TABLE IF EXISTS fact_monthly_usage;")
    cursor.execute("DROP TABLE IF EXISTS fact_subscriptions;")
    cursor.execute("DROP TABLE IF EXISTS dim_customers;")
    cursor.execute("DROP TABLE IF EXISTS dim_plans;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # 1. dim_plans
    cursor.execute("""
    CREATE TABLE dim_plans (
        plan_id INT AUTO_INCREMENT PRIMARY KEY,
        plan_name VARCHAR(50) NOT NULL UNIQUE,
        tier VARCHAR(20) NOT NULL,
        monthly_price DECIMAL(10,2) NOT NULL,
        storage_limit_gb INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)

    # 2. dim_customers
    cursor.execute("""
    CREATE TABLE dim_customers (
        customer_id VARCHAR(20) PRIMARY KEY,
        company_size VARCHAR(30) NOT NULL,
        industry VARCHAR(50) NOT NULL,
        region VARCHAR(30) NOT NULL,
        account_channel VARCHAR(50) NOT NULL,
        signup_date DATE NOT NULL,
        is_active_flag TINYINT(1) DEFAULT 1
    ) ENGINE=InnoDB;
    """)

    # 3. fact_subscriptions
    cursor.execute("""
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
    """)

    # 4. fact_monthly_usage
    cursor.execute("""
    CREATE TABLE fact_monthly_usage (
        usage_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id VARCHAR(20) NOT NULL,
        usage_year_month INT NOT NULL,
        teams_active_pct DECIMAL(5,2) NOT NULL,
        onedrive_gb_used DECIMAL(10,2) NOT NULL,
        support_tickets_raised INT DEFAULT 0,
        CONSTRAINT fk_fact_usage_cust FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
    ) ENGINE=InnoDB;
    """)

    # Indexes
    cursor.execute("CREATE INDEX idx_fact_sub_churn ON fact_subscriptions(churn_status_flag, mrr_amount, customer_id);")
    cursor.execute("CREATE INDEX idx_dim_cust_ind ON dim_customers(industry, region);")
    cursor.execute("CREATE INDEX idx_fact_usage_cust ON fact_monthly_usage(customer_id, usage_year_month);")

    print("Loading data from CSVs...")
    df_plans = pd.read_csv(os.path.join(DATA_DIR, "dim_plans.csv"))
    plan_records = df_plans[["plan_id", "plan_name", "tier", "monthly_price", "storage_limit_gb"]].values.tolist()
    cursor.executemany(
        "INSERT INTO dim_plans (plan_id, plan_name, tier, monthly_price, storage_limit_gb) VALUES (%s, %s, %s, %s, %s);",
        plan_records
    )

    df_cust = pd.read_csv(os.path.join(DATA_DIR, "dim_customers.csv"))
    dim_cust_records = [
        (
            r["customer_id"], r["company_size"], r["industry"], r["region"],
            r["account_channel"], r["signup_date"], int(1 - r["churned"])
        )
        for _, r in df_cust.iterrows()
    ]
    cursor.executemany(
        "INSERT INTO dim_customers (customer_id, company_size, industry, region, account_channel, signup_date, is_active_flag) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        dim_cust_records
    )

    plan_map = dict(zip(df_plans["plan_name"], df_plans["plan_id"]))
    fact_sub_records = [
        (
            1001 + idx, r["customer_id"], plan_map[r["plan_name"]], int(r["license_count"]),
            float(r["discount_pct"]), float(r["mrr"]), int(r["auto_renewal"]),
            int(r["copilot_enabled"]), int(r["churned"]),
            "2026-07-01" if r["churned"] == 1 else None
        )
        for idx, r in df_cust.iterrows()
    ]
    cursor.executemany(
        """INSERT INTO fact_subscriptions (
            subscription_id, customer_id, plan_id, license_count, discount_pct,
            mrr_amount, auto_renewal_flag, copilot_addon_flag, churn_status_flag, churn_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
        fact_sub_records
    )

    fact_usage_records = [
        (1 + idx, r["customer_id"], 202607, float(r["teams_adoption_pct"]), float(r["onedrive_gb"]), int(r["support_tickets"]))
        for idx, r in df_cust.iterrows()
    ]
    cursor.executemany(
        """INSERT INTO fact_monthly_usage (
            usage_id, customer_id, usage_year_month, teams_active_pct, onedrive_gb_used, support_tickets_raised
        ) VALUES (%s, %s, %s, %s, %s, %s);""",
        fact_usage_records
    )

    conn.commit()

    print("\nData loaded successfully! Table statistics:")
    for tbl in ["dim_plans", "dim_customers", "fact_subscriptions", "fact_monthly_usage"]:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        print(f"  * {tbl}: {cursor.fetchone()[0]:,} records")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    setup_and_load_mysql()
