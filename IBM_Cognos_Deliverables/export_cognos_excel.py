"""
export_cognos_excel.py
======================
Compiles all individual VeriNews AI Cognos CSV datasets into a single,
multi-tab Excel workbook (VeriNews_Cognos_Datasets.xlsx) compatible with
IBM Cognos Analytics, Microsoft Power BI, and Tableau.
"""

import os
import pandas as pd

def compile_excel():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_excel = os.path.join(base_dir, "VeriNews_Cognos_Datasets.xlsx")

    csv_files = {
        "KPI_Summary": "cognos_kpi_summary.csv",
        "Dataset_Distribution": "cognos_dataset_distribution.csv",
        "Model_Performance": "cognos_model_performance.csv",
        "Confusion_Matrix": "cognos_confusion_matrix.csv",
        "Bias_and_Leakage_Audit": "cognos_dataset_bias_audit.csv",
        "Scan_History_Telemetry": "cognos_scan_intelligence_history.csv",
    }

    try:
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
            for sheet_name, filename in csv_files.items():
                csv_path = os.path.join(base_dir, filename)
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"Added sheet: {sheet_name} ({len(df)} rows)")
                else:
                    print(f"Warning: {filename} not found.")
        print(f"\nSuccessfully generated multi-sheet Cognos workbook: {output_excel}")
    except Exception as e:
        print(f"Error compiling Excel: {e}")

if __name__ == "__main__":
    compile_excel()
