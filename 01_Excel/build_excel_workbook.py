import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "data", "dim_customers.csv")
df = pd.read_csv(csv_path)

excel_path = os.path.join(base_dir, "01_Excel", "Microsoft_365_SaaS_Analytics.xlsx")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Styles & Colors (Microsoft Fluent / Office Palette)
navy_header_fill = PatternFill(start_color="004578", end_color="004578", fill_type="solid")
blue_sub_fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
card_fill = PatternFill(start_color="F3F9FD", end_color="F3F9FD", fill_type="solid")
zebra_fill = PatternFill(start_color="FAFAFA", end_color="FAFAFA", fill_type="solid")
accent_green_fill = PatternFill(start_color="DFF6DD", end_color="DFF6DD", fill_type="solid")
accent_red_fill = PatternFill(start_color="FDE7E9", end_color="FDE7E9", fill_type="solid")

font_title = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
font_sub = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_kpi_val = Font(name="Segoe UI", size=18, bold=True, color="004578")
font_kpi_lbl = Font(name="Segoe UI", size=9, bold=True, color="605E5C")
font_regular = Font(name="Segoe UI", size=10)
font_bold = Font(name="Segoe UI", size=10, bold=True)

thin_border = Border(
    left=Side(style='thin', color='E1DFDD'),
    right=Side(style='thin', color='E1DFDD'),
    top=Side(style='thin', color='E1DFDD'),
    bottom=Side(style='thin', color='E1DFDD')
)

# ==========================================
# SHEET 1: EXECUTIVE KPI DASHBOARD
# ==========================================
ws1 = wb.create_sheet(title="Executive Dashboard")
ws1.views.sheetView[0].showGridLines = True

# Title Banner
ws1.merge_cells("A1:H2")
ws1["A1"] = "MICROSOFT 365 SaaS SUBSCRIPTION & REVENUE ANALYTICS"
ws1["A1"].font = font_title
ws1["A1"].fill = navy_header_fill
ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")

# KPI Summary Cards (Rows 4-6)
cards = [
    ("B4:C5", "TOTAL ANNUAL RECURRING REVENUE (ARR)", "=$F$15*12", "$#,##0"),
    ("D4:E5", "TOTAL ACTIVE CUSTOMERS", "=COUNTA('Customer Data'!A2:A5001)", "#,##0"),
    ("F4:F5", "PORTFOLIO CHURN RATE", "=$G$15", "0.00%"),
    ("G4:H5", "AVERAGE REVENUE PER USER (ARPU)", "=$F$15/$D$5", "$#,##0.00")
]

for cell_range, label, formula, num_format in cards:
    top_left = cell_range.split(":")[0]
    ws1.merge_cells(cell_range)
    ws1[top_left] = formula
    ws1[top_left].font = font_kpi_val
    ws1[top_left].alignment = Alignment(horizontal="center", vertical="center")
    ws1[top_left].fill = card_fill
    ws1[top_left].number_format = num_format
    
    # Border for the merged card
    start_col, start_row = openpyxl.utils.coordinate_to_tuple(top_left)
    end_col, end_row = openpyxl.utils.coordinate_to_tuple(cell_range.split(":")[1])
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            ws1.cell(row=r, column=c).border = thin_border
            ws1.cell(row=r, column=c).fill = card_fill

    # Label below card
    lbl_cell = ws1.cell(row=6, column=start_col)
    lbl_cell.value = label
    lbl_cell.font = font_kpi_lbl
    lbl_cell.alignment = Alignment(horizontal="center", vertical="center")

# Plan Breakdown Table (Rows 8-15)
ws1.merge_cells("A8:H8")
ws1["A8"] = "SUBSCRIPTION PLAN REVENUE & RETENTION BREAKDOWN"
ws1["A8"].font = font_sub
ws1["A8"].fill = blue_sub_fill
ws1["A8"].alignment = Alignment(horizontal="left", vertical="center", indent=1)

headers = ["Plan Name", "License Tier", "Base Price", "Active Accounts", "Total Licenses", "Total MRR", "Churn Rate", "Teams %"]
for col_idx, h in enumerate(headers, start=1):
    cell = ws1.cell(row=9, column=col_idx, value=h)
    cell.font = font_bold
    cell.fill = PatternFill(start_color="EDEBE9", end_color="EDEBE9", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = thin_border

plan_rows = [
    ("M365 Business Basic", "SMB", 6.00),
    ("M365 Business Standard", "SMB", 12.50),
    ("M365 Business Premium", "SMB", 22.00),
    ("M365 E3", "Enterprise", 36.00),
    ("M365 E5", "Enterprise", 57.00),
]

for idx, (pname, tier, price) in enumerate(plan_rows, start=10):
    ws1.cell(row=idx, column=1, value=pname).font = font_bold
    ws1.cell(row=idx, column=2, value=tier).alignment = Alignment(horizontal="center")
    ws1.cell(row=idx, column=3, value=price).number_format = "$#,##0.00"
    
    # Formulas referencing Customer Data sheet
    ws1.cell(row=idx, column=4, value=f"=COUNTIF('Customer Data'!$G$2:$G$5001, A{idx})").number_format = "#,##0"
    ws1.cell(row=idx, column=5, value=f"=SUMIF('Customer Data'!$G$2:$G$5001, A{idx}, 'Customer Data'!$I$2:$I$5001)").number_format = "#,##0"
    ws1.cell(row=idx, column=6, value=f"=SUMIF('Customer Data'!$G$2:$G$5001, A{idx}, 'Customer Data'!$K$2:$K$5001)").number_format = "$#,##0"
    ws1.cell(row=idx, column=7, value=f"=AVERAGEIFS('Customer Data'!$R$2:$R$5001, 'Customer Data'!$G$2:$G$5001, A{idx})").number_format = "0.00%"
    ws1.cell(row=idx, column=8, value=f"=AVERAGEIFS('Customer Data'!$M$2:$M$5001, 'Customer Data'!$G$2:$G$5001, A{idx})/100").number_format = "0.0%"
    
    for c in range(1, 9):
        ws1.cell(row=idx, column=c).border = thin_border

# Total Summary Row
ws1.cell(row=15, column=1, value="Total Portfolio Summary").font = font_bold
ws1.cell(row=15, column=4, value="=SUM(D10:D14)").number_format = "#,##0"
ws1.cell(row=15, column=5, value="=SUM(E10:E14)").number_format = "#,##0"
ws1.cell(row=15, column=6, value="=SUM(F10:F14)").number_format = "$#,##0"
ws1.cell(row=15, column=7, value="=AVERAGE('Customer Data'!$R$2:$R$5001)").number_format = "0.00%"
ws1.cell(row=15, column=8, value="=AVERAGE('Customer Data'!$M$2:$M$5001)/100").number_format = "0.0%"

for c in range(1, 9):
    ws1.cell(row=15, column=c).font = font_bold
    ws1.cell(row=15, column=c).fill = PatternFill(start_color="F3F2F1", end_color="F3F2F1", fill_type="solid")
    ws1.cell(row=15, column=c).border = thin_border

# ==========================================
# SHEET 2: CUSTOMER DATA (STAGING)
# ==========================================
ws2 = wb.create_sheet(title="Customer Data")
ws2.views.sheetView[0].showGridLines = True

data_headers = list(df.columns)
for col_idx, h in enumerate(data_headers, start=1):
    c = ws2.cell(row=1, column=col_idx, value=h)
    c.font = font_bold
    c.fill = blue_sub_fill
    c.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    c.alignment = Alignment(horizontal="center")

for r_idx, row in df.iterrows():
    row_num = r_idx + 2
    for c_idx, val in enumerate(row, start=1):
        ws2.cell(row=row_num, column=c_idx, value=val)

# ==========================================
# SHEET 3: DYNAMIC CUSTOMER LOOKUP TOOL
# ==========================================
ws3 = wb.create_sheet(title="Customer Lookup Tool")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A1:F2")
ws3["A1"] = "ACCOUNT PROFILE & CHURN RISK LOOKUP (XLOOKUP ENGINE)"
ws3["A1"].font = font_title
ws3["A1"].fill = navy_header_fill
ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")

ws3["B4"] = "Enter Customer ID:"
ws3["B4"].font = font_bold
ws3["C4"] = "MS-10042"
ws3["C4"].font = Font(name="Segoe UI", size=12, bold=True, color="0078D4")
ws3["C4"].fill = PatternFill(start_color="FFF4CE", end_color="FFF4CE", fill_type="solid")
ws3["C4"].alignment = Alignment(horizontal="center")
ws3["C4"].border = thin_border

fields = [
    ("B6", "Plan Name:", "=XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!G:G, \"Not Found\")"),
    ("B7", "Company Size:", "=XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!B:B, \"Not Found\")"),
    ("B8", "Industry Sector:", "=XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!C:C, \"Not Found\")"),
    ("B9", "Monthly Revenue (MRR):", "=XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!K:K, 0)"),
    ("B10", "Teams Adoption Rate:", "=XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!M:M, 0)&\"%\""),
    ("B11", "Support Tickets Raised:", "=XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!O:O, 0)"),
    ("B12", "Copilot AI Enabled:", "=IF(XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!P:P, 0)=1, \"YES (Active)\", \"NO\")"),
    ("B13", "Churn Status:", "=IF(XLOOKUP(C4, 'Customer Data'!A:A, 'Customer Data'!R:R, 0)=1, \"CHURNED\", \"ACTIVE / RETAINED\")")
]

for lbl_pos, lbl_text, form in fields:
    row_n = int(lbl_pos[1:])
    ws3[lbl_pos] = lbl_text
    ws3[lbl_pos].font = font_bold
    
    val_pos = f"C{row_n}"
    ws3[val_pos] = form
    ws3[val_pos].font = font_regular
    ws3[val_pos].border = thin_border
    if row_n == 9:
        ws3[val_pos].number_format = "$#,##0.00"

# ==========================================
# SHEET 4: WHAT-IF SENSITIVITY MODEL
# ==========================================
ws4 = wb.create_sheet(title="Churn Sensitivity Model")
ws4.views.sheetView[0].showGridLines = True

ws4.merge_cells("A1:F2")
ws4["A1"] = "WHAT-IF CHURN REDUCTION & REVENUE PRESERVATION MODEL"
ws4["A1"].font = font_title
ws4["A1"].fill = navy_header_fill
ws4["A1"].alignment = Alignment(horizontal="center", vertical="center")

ws4["B4"] = "Current Annual Revenue (ARR):"
ws4["B4"].font = font_bold
ws4["C4"] = "='Executive Dashboard'!F15*12"
ws4["C4"].font = font_bold
ws4["C4"].number_format = "$#,##0"

ws4["B5"] = "Current Baseline Churn Rate:"
ws4["B5"].font = font_bold
ws4["C5"] = "='Executive Dashboard'!G15"
ws4["C5"].font = font_bold
ws4["C5"].number_format = "0.00%"

sens_headers = ["Churn Reduction Target", "New Churn Rate", "Retained Accounts (Annual)", "Annual Revenue Preserved ($)"]
for c_idx, h in enumerate(sens_headers, start=2):
    c = ws4.cell(row=7, column=c_idx, value=h)
    c.font = font_bold
    c.fill = blue_sub_fill
    c.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    c.alignment = Alignment(horizontal="center")

sens_scenarios = [0.005, 0.010, 0.020, 0.030, 0.050]
for idx, target_reduction in enumerate(sens_scenarios, start=8):
    ws4.cell(row=idx, column=2, value=target_reduction).number_format = "0.0%"
    ws4.cell(row=idx, column=3, value=f"=C$5-B{idx}").number_format = "0.00%"
    ws4.cell(row=idx, column=4, value=f"=ROUND(B{idx}*'Executive Dashboard'!D15, 0)").number_format = "#,##0"
    ws4.cell(row=idx, column=5, value=f"=D{idx}*('Executive Dashboard'!F15/'Executive Dashboard'!D15)*12").number_format = "$#,##0"
    
    for col in range(2, 6):
        ws4.cell(row=idx, column=col).border = thin_border
        ws4.cell(row=idx, column=col).fill = zebra_fill if idx % 2 == 0 else PatternFill(fill_type=None)

# Adjust Column Widths Across Sheets
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len and not cell.coordinate in sheet.merged_cells:
                max_len = len(val_str)
        sheet.column_dimensions[col_letter].width = max(max_len + 4, 14)

wb.save(excel_path)
print(f"Excel workbook built with 4 interactive sheets: {excel_path}")
