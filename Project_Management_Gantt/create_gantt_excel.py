"""
create_gantt_excel.py
=====================
Generates a Gantt-ready Excel workbook (VeriNews_Project_Gantt_Chart.xlsx)
from verinews_project_gantt_schedule.csv with task timelines and completion flags.
"""

import os
import pandas as pd

def compile_gantt_excel():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, "verinews_project_gantt_schedule.csv")
    output_excel = os.path.join(base_dir, "VeriNews_Project_Gantt_Chart.xlsx")

    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return

    df = pd.read_csv(input_csv)
    try:
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Gantt_Schedule", index=False)
        print(f"Successfully generated Gantt Excel workbook: {output_excel}")
    except Exception as e:
        print(f"Error compiling Gantt Excel: {e}")

if __name__ == "__main__":
    compile_gantt_excel()
