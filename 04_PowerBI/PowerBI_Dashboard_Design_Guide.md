# 📊 Microsoft 365 SaaS Performance Dashboard Blueprint

This blueprint outlines how to build the modern **Executive Performance Dashboard** for the **Microsoft 365 SaaS Subscription & Customer Churn Analytics** project.

---

## ⚡ 1-Click Fast Connect

1. Double-click [`Microsoft_365_Excel_Connection.pbids`](file:///D:/New%20folder/PK/DATA%20ANALYST/Microsoft_Data_Analytics_Project/04_PowerBI/Microsoft_365_Excel_Connection.pbids) to open Power BI Desktop directly connected to the workbook [`Microsoft_365_SaaS_Analytics.xlsx`](file:///D:/New%20folder/PK/DATA%20ANALYST/Microsoft_Data_Analytics_Project/01_Excel/Microsoft_365_SaaS_Analytics.xlsx).
2. Select `Dim_Customers`, `Dim_Plans`, `Fact_Subscriptions`, and `Fact_Monthly_Usage`.
3. Click **Load**.

---

## 🎨 Step 1: Apply the Matching Modern Theme

We created a custom theme file matching the soft-blue background, rounded corners, card drop shadows, and Microsoft brand palette:
[`Microsoft_365_Modern_Theme.json`](file:///D:/New%20folder/PK/DATA%20ANALYST/Microsoft_Data_Analytics_Project/04_PowerBI/Microsoft_365_Modern_Theme.json)

1. In **Power BI Desktop**, go to the **View** tab on the top ribbon.
2. Click the **Themes** dropdown gallery > select **Browse for themes...** at the bottom.
3. Select:
   `D:\New folder\PK\DATA ANALYST\Microsoft_Data_Analytics_Project\04_PowerBI\Microsoft_365_Modern_Theme.json`
4. Click **Open**. Your canvas will adopt the matching soft-blue background (`#EDF2F9`), rounded card corners, and modern palette!

---

## 📐 Step 2: The Right-Hand Blue Filter Sidebar

1. Go to **Insert** tab > **Shapes** > click **Rectangle**.
2. Position it along the right edge:
   - Width: ~18% of canvas width.
   - Height: 100% of canvas height.
3. In **Format Shape**:
   - **Fill color**: `#0078D4` (Microsoft Blue) or `#005A9E`.
   - **Border**: Off.
   - **Rounded corners**: `12px`.
4. Add a **Text Box** at the top:
   - Text: `☁️ Microsoft 365 Analytics` (White font, Bold, 16pt).
5. Add **Slicers** inside the blue panel:
   - **Slicer 1**: `Dim_Plans[plan_name]` (M365 E5, M365 E3, Business Standard, Business Premium, Business Basic).
   - **Slicer 2**: `Dim_Customers[industry]` (Healthcare, Manufacturing, Tech, Finance, Retail, Education).
   - **Slicer 3**: `Fact_Subscriptions[copilot_addon_flag]` (1 = Copilot Enabled, 0 = Non-Copilot).
   - **Slicer 4**: `Dim_Customers[region]` (North America, EMEA, APAC, LATAM).

---

## 💳 Step 3: The 12 Top KPI Cards (2 Rows of 6)

Create each card using the **Card** visual, and set the **Background color** in **Format visual > General > Effects > Background**:

### Row 1 (Financials & Customer Scale):
| Card Position | Measure Field | Value | Card Fill Color | Font Color |
| :--- | :--- | :--- | :--- | :--- |
| **1. Top-Left** | `[Total ARR]` | **$445.8M** | Deep Navy (`#25287A`) | White |
| **2.** | `[Active MRR]` | **$34.3M** | Royal Blue (`#3954DF`) | White |
| **3.** | `[Active Customers]` | **4,610** | Teal / Cyan (`#009CA6`) | White |
| **4.** | `[Licensed Seats]` | **1.96M** | Emerald Green (`#00A66D`) | White |
| **5.** | `[Copilot Adoption %]` | **38.18%** | Rose Pink / Magenta (`#D82F79`) | White |
| **6.** | `[Average ARPU]` | **$7,437** | Vibrant Purple (`#753BF4`) | White |

### Row 2 (Retention Dynamics & Churn Risk):
| Card Position | Measure Field | Value | Card Fill Color | Font Color |
| :--- | :--- | :--- | :--- | :--- |
| **7.** | `[Portfolio Churn %]` | **7.80%** | Deep Navy (`#25287A`) | White |
| **8.** | `[Copilot Churn %]` | **3.61%** | Royal Blue (`#3954DF`) | White / Mint |
| **9.** | `[Non-Copilot Churn %]` | **10.38%** | Teal / Cyan (`#009CA6`) | White / Coral |
| **10.** | `[Copilot Churn Lift]` | **-65.2%** | Emerald Green (`#00A66D`) | White |
| **11.** | `[Churned ARR (Lost)]`| **$34.4M** | Rose Pink / Magenta (`#D82F79`) | White |
| **12.** | `[High-Risk Accounts]` | **51** | Vibrant Purple (`#753BF4`) | White |

---

## 📊 Step 4: The 7 Core Analytical Visuals

### 1. ARR by Plan Tier (Middle-Left Donut Chart)
- **Visual**: **Donut chart**
- **Legend**: `Dim_Plans[plan_name]`
- **Values**: `[Total ARR]`
- *Insight:* Enterprise tiers (`M365 E5` at $118.8M and `M365 E3` at $116.7M) contribute **52.8% of total revenue**.

### 2. Copilot AI Churn Impact (Middle-Center Bar Chart)
- **Visual**: **Clustered column chart**
- **X-axis**: Copilot Status (Enabled vs Disabled)
- **Y-axis**: `[Portfolio Churn Rate %]`
- *Format:* Green bar for Copilot (3.61%), Red bar for Non-Copilot (10.38%).
- *Key Takeaway:* Copilot drives a **65.2% reduction in churn** ($\chi^2 = 74.28, p < 0.001$).

### 3. Industry ARR Distribution (Middle-Right Stacked Column)
- **Visual**: **Stacked column chart**
- **X-axis**: `Dim_Customers[industry]`
- **Y-axis**: `[Total ARR]`
- **Legend**: Churn Status (Active vs Churned)
- *Insight:* Healthcare ($82.2M) and Manufacturing ($76.1M) lead total revenue.

### 4. Global Geographic ARR (Bottom-Left Bar Chart)
- **Visual**: **Horizontal Bar chart** or **Filled Map**
- **Y-axis / Location**: `Dim_Customers[region]`
- **X-axis / Bubble size**: `[Total ARR]`
- *Insight:* North America ($205.3M) and EMEA ($128.4M) account for **74.8% of global revenue**.

### 5. Monthly Retention Trajectory (Bottom-Center Line Chart)
- **Visual**: **Line chart**
- **X-axis**: Date (Quarter / Month)
- **Y-axis**: Customer Retention Rate (%)
- *Format:* Emerald Green line with subtle area fill.

### 6. Early Warning Churn Risk Matrix Table (Bottom-Right Matrix)
- **Visual**: **Table**
- **Columns**: `customer_id`, `plan_name`, `teams_active_pct`, `support_tickets_raised`, `mrr_amount`
- **Filter**: `teams_active_pct < 35%` and `support_tickets_raised >= 3`
- *Actionable Finding:* Flags the **51 critical accounts ($4.85M ARR at risk)** with a **25.49% churn probability** for proactive CSM outreach!
