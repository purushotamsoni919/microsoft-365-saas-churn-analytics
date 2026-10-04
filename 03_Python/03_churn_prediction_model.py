import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
charts_dir = os.path.join(base_dir, "03_Python", "charts")

csv_path = os.path.join(base_dir, "data", "dim_customers.csv")
df = pd.read_csv(csv_path)

# 1. Feature Engineering
features = ['license_count', 'mrr', 'tenure_months', 'teams_adoption_pct', 
            'onedrive_gb', 'support_tickets', 'copilot_enabled', 'auto_renewal', 'discount_pct']
target = 'churned'

X = df[features].copy()
y = df[target].copy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# 2. Train Random Forest Model
rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)
y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

auc_score = roc_auc_score(y_test, y_pred_proba)
print(f"=== MACHINE LEARNING MODEL PERFORMANCE ===")
print(f"Random Forest ROC-AUC Score: {auc_score:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 3. Feature Importance
importances = pd.Series(rf_model.feature_importances_, index=features).sort_values(ascending=False)
print("Top Predictive Churn Drivers:")
print(importances)

# 4. Save Feature Importance Chart
plt.figure(figsize=(9, 5))
importances.plot(kind='barh', color='#0078d4')
plt.title('Microsoft 365 SaaS Churn - Key Predictive Drivers (Feature Importance)', fontweight='bold')
plt.xlabel('Relative Importance')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, "rf_feature_importance.png"), dpi=300)
plt.close()

# 5. Score entire dataset for Power BI & Excel ingestion
full_probabilities = rf_model.predict_proba(X)[:, 1]
df['churn_probability'] = np.round(full_probabilities, 3)
df['churn_risk_tier'] = pd.cut(
    df['churn_probability'], 
    bins=[-0.01, 0.20, 0.50, 1.0], 
    labels=['Low Risk', 'Medium Risk', 'High Risk']
)

output_scored_csv = os.path.join(base_dir, "data", "dim_customers_scored.csv")
df.to_csv(output_scored_csv, index=False)
print(f"\nScored dataset with Risk Tiers saved to: {output_scored_csv}")
