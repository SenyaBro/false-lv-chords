import pandas as pd
import re

files = [
    (r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\набор данных для докторской диссертации 23_03_20.xls', 'doctoral_dataset'),
    (r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ЭхоКГ и ЭКГ ОВЗ и здоровые 2026 (1).xlsx', 'echo_ecg'),
    (r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\final_dataset_15_04.xlsx', 'final_dataset_15_04')
]

for path, name in files:
    try:
        df = pd.read_excel(path)
        print(f"\n--- {name} (Rows: {len(df)}) ---")
        for col in df.columns:
            if not isinstance(col, str): continue
            
            # Print any column that might remotely mean "chord" or "лс" or "tendon" or "mid" or "basal" or "obl" or "trans"
            if re.search(r'ЛС|хорд|chord|tendon|obl|trans|mid|basal|апик|срд|баз|ср|попер|кос|лж|ARS', col, re.IGNORECASE):
                non_null = df[col].notna().sum()
                print(f"  POTENTIAL: '{col}' ({non_null} non-nulls)")
    except Exception as e:
        print(f"Error reading {name}: {e}")

