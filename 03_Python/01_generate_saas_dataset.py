import os
import sys
import numpy as np
import pandas as pd
import datetime
import sqlite3
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(base_dir, "01_Excel"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "02_SQL"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "03_Python"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "04_PowerBI"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "presentation"), exist_ok=True)

print("Directories created.")

# ==========================================
# 1. GENERATE REALISTIC DATASET (5,000 CUSTOMERS)
# ==========================================
np.random.seed(42)
n_customers = 5000

customer_ids = [f"MS-{10000 + i}" for i in range(n_customers)]
regions = np.random.choice(["North America", "EMEA", "APAC", "LATAM"], size=n_customers, p=[0.45, 0.30, 0.18, 0.07])
industries = np.random.choice(["Technology", "Healthcare", "Financial Services", "Retail", "Manufacturing", "Education"], size=n_customers)
company_sizes = np.random.choice(["SMB (1-50)", "Mid-Market (51-500)", "Enterprise (500+)"], size=n_customers, p=[0.50, 0.35, 0.15])
account_managers = np.random.choice(["Satya Nadella Team", "Azure Enterprise Group", "Commercial Partner Org", "Direct Digital"], size=n_customers)

plans = ["M365 Business Basic", "M365 Business Standard", "M365 Business Premium", "M365 E3", "M365 E5"]
plan_prices = {"M365 Business Basic": 6.00, "M365 Business Standard": 12.50, "M365 Business Premium": 22.00, "M365 E3": 36.00, "M365 E5": 57.00}

assigned_plans = np.random.choice(plans, size=n_customers, p=[0.25, 0.30, 0.20, 0.15, 0.10])
license_counts = np.where(
    company_sizes == "SMB (1-50)", np.random.randint(5, 50, size=n_customers),
    np.where(company_sizes == "Mid-Market (51-500)", np.random.randint(51, 500, size=n_customers), np.random.randint(501, 3500, size=n_customers))
)

# Signup dates over the last 24 months
start_date = datetime.date(2024, 9, 1)
end_date = datetime.date(2026, 8, 1)
days_between = (end_date - start_date).days

signup_days = np.random.randint(0, days_between, size=n_customers)
signup_dates = [start_date + datetime.timedelta(days=int(d)) for d in signup_days]

# Tenure & Usage telemetry
tenure_months = [max(1, int((end_date - d).days / 30.4)) for d in signup_dates]
teams_active_users_pct = np.clip(np.random.normal(0.68, 0.18, size=n_customers), 0.05, 1.0)
onedrive_storage_gb = np.clip(np.random.exponential(120, size=n_customers) * (license_counts / 10), 10, 50000)
support_tickets_raised = np.random.poisson(lam=1.8, size=n_customers)
copilot_license_active = np.random.choice([1, 0], size=n_customers, p=[0.38, 0.62])
auto_renewal_enabled = np.random.choice([1, 0], size=n_customers, p=[0.82, 0.18])
discount_applied_pct = np.random.choice([0.0, 0.10, 0.15, 0.20], size=n_customers, p=[0.55, 0.25, 0.12, 0.08])

# Churn logic driven by engagement, support tickets, and renewal status
churn_prob = (
    0.08 
    + (1.0 - teams_active_users_pct) * 0.35 
    + (support_tickets_raised > 4) * 0.25 
    - (copilot_license_active * 0.15) 
    - (auto_renewal_enabled * 0.18)
    + (tenure_months < np.median(tenure_months)) * 0.05
)
churn_prob = np.clip(churn_prob, 0.02, 0.95)
churned = (np.random.rand(n_customers) < churn_prob).astype(int)

# Monthly recurring revenue (MRR)
unit_prices = np.array([plan_prices[p] for p in assigned_plans])
mrr = license_counts * unit_prices * (1 - discount_applied_pct)

df_customers = pd.DataFrame({
    "customer_id": customer_ids,
    "company_size": company_sizes,
    "industry": industries,
    "region": regions,
    "account_channel": account_managers,
    "signup_date": signup_dates,
    "plan_name": assigned_plans,
    "unit_price": unit_prices,
    "license_count": license_counts,
    "discount_pct": discount_applied_pct,
    "mrr": np.round(mrr, 2),
    "tenure_months": tenure_months,
    "teams_adoption_pct": np.round(teams_active_users_pct * 100, 1),
    "onedrive_gb": np.round(onedrive_storage_gb, 1),
    "support_tickets": support_tickets_raised,
    "copilot_enabled": copilot_license_active,
    "auto_renewal": auto_renewal_enabled,
    "churned": churned
})

# Save CSV datasets
df_customers.to_csv(os.path.join(base_dir, "data", "dim_customers.csv"), index=False)

# Create Plans Dimension
df_plans = pd.DataFrame([
    {"plan_id": 1, "plan_name": "M365 Business Basic", "tier": "SMB", "monthly_price": 6.00, "storage_limit_gb": 1000},
    {"plan_id": 2, "plan_name": "M365 Business Standard", "tier": "SMB", "monthly_price": 12.50, "storage_limit_gb": 1000},
    {"plan_id": 3, "plan_name": "M365 Business Premium", "tier": "SMB", "monthly_price": 22.00, "storage_limit_gb": 1000},
    {"plan_id": 4, "plan_name": "M365 E3", "tier": "Enterprise", "monthly_price": 36.00, "storage_limit_gb": 5000},
    {"plan_id": 5, "plan_name": "M365 E5", "tier": "Enterprise", "monthly_price": 57.00, "storage_limit_gb": 5000},
])
df_plans.to_csv(os.path.join(base_dir, "data", "dim_plans.csv"), index=False)

# Save SQLite Database for immediate SQL practice
db_path = os.path.join(base_dir, "data", "m365_analytics.db")
conn = sqlite3.connect(db_path)
df_customers.to_sql("customers", conn, if_exists="replace", index=False)
df_plans.to_sql("plans", conn, if_exists="replace", index=False)
conn.close()

print(f"Data generated: {len(df_customers)} records saved to CSV and SQLite DB.")
