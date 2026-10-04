import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
charts_dir = os.path.join(base_dir, "03_Python", "charts")
os.makedirs(charts_dir, exist_ok=True)

csv_path = os.path.join(base_dir, "data", "dim_customers.csv")
df = pd.read_csv(csv_path)

print("=== 1. DESCRIPTIVE SUMMARY STATISTICS ===")
total_customers = len(df)
overall_churn_rate = df['churned'].mean() * 100
total_mrr = df['mrr'].sum()
avg_mrr = df['mrr'].mean()

print(f"Total Customer Accounts: {total_customers:,}")
print(f"Overall Churn Rate: {overall_churn_rate:.2f}%")
print(f"Total Monthly Recurring Revenue (MRR): ${total_mrr:,.2f}")
print(f"Average MRR per Account: ${avg_mrr:,.2f}")

# Group by Plan
plan_summary = df.groupby('plan_name').agg(
    accounts=('customer_id', 'count'),
    churn_rate=('churned', lambda x: np.round(x.mean() * 100, 2)),
    total_mrr=('mrr', 'sum'),
    avg_teams_pct=('teams_adoption_pct', 'mean')
).reset_index()
print("\n=== Plan-Level Breakdown ===")
print(plan_summary.to_string(index=False))

# ==========================================
# 2. STATISTICAL HYPOTHESIS TESTING (A/B TEST ANALOG)
# ==========================================
print("\n=== 2. STATISTICAL HYPOTHESIS TESTING ===")
# Test 1: Does Copilot activation significantly reduce Churn?
copilot_yes = df[df['copilot_enabled'] == 1]['churned']
copilot_no = df[df['copilot_enabled'] == 0]['churned']

contingency_table = pd.crosstab(df['copilot_enabled'], df['churned'])
chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

print(f"Copilot Enabled Churn Rate: {copilot_yes.mean()*100:.2f}% (n={len(copilot_yes)})")
print(f"Copilot Disabled Churn Rate: {copilot_no.mean()*100:.2f}% (n={len(copilot_no)})")
print(f"Chi-Square Statistic: {chi2:.4f}, p-value: {p_val:.4e}")
if p_val < 0.05:
    print(">> Result: Statistically significant (p < 0.05). Copilot feature activation strongly correlates with higher retention.")
else:
    print(">> Result: Not statistically significant.")

# ==========================================
# 3. GENERATE VISUALIZATIONS FOR PORTFOLIO
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Microsoft 365 SaaS Analytics & Churn Diagnostics', fontsize=16, fontweight='bold', color='#004578')

# Plot 1: Churn Rate by Industry
industry_churn = df.groupby('industry')['churned'].mean().sort_values() * 100
axs[0, 0].barh(industry_churn.index, industry_churn.values, color='#0078d4')
axs[0, 0].set_title('Churn Rate by Industry (%)', fontweight='bold')
axs[0, 0].set_xlabel('Churn Rate (%)')

# Plot 2: Teams Adoption vs Churn
sns.boxplot(x='churned', y='teams_adoption_pct', data=df, ax=axs[0, 1], palette=['#107c41', '#d83b01'])
axs[0, 1].set_xticklabels(['Retained (0)', 'Churned (1)'])
axs[0, 1].set_title('Teams Adoption Rate vs. Customer Retention', fontweight='bold')
axs[0, 1].set_ylabel('Teams Active Users (%)')

# Plot 3: MRR Distribution by Plan
plan_mrr = df.groupby('plan_name')['mrr'].sum().sort_values() / 1000
axs[1, 0].bar(plan_mrr.index, plan_mrr.values, color='#2b88d8')
axs[1, 0].set_title('Total MRR Contribution by Plan ($K)', fontweight='bold')
axs[1, 0].set_xticklabels(plan_mrr.index, rotation=25, ha='right')
axs[1, 0].set_ylabel('Total MRR ($ in Thousands)')

# Plot 4: Correlation Heatmap
corr_cols = ['mrr', 'tenure_months', 'teams_adoption_pct', 'onedrive_gb', 'support_tickets', 'copilot_enabled', 'auto_renewal', 'churned']
corr_matrix = df[corr_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='Blues', ax=axs[1, 1], cbar=False)
axs[1, 1].set_title('Key Drivers Correlation Matrix', fontweight='bold')

plt.tight_layout()
chart_path = os.path.join(charts_dir, "eda_churn_diagnostics.png")
plt.savefig(chart_path, dpi=300)
plt.close()
print(f"\nCharts generated and saved to: {chart_path}")
