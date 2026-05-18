import pandas as pd
import os

files = {
    'table_const_csv': r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\output\final_analysis_dataset.csv',
    'table_const_xlsx': r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\output\final_analysis_dataset.xlsx',
    'false_new_xlsx': r'c:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_new.xlsx',
    'false_old_xlsx': r'c:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_old.xlsx',
}

for name, path in files.items():
    print(f"\n--- {name} ---")
    if not os.path.exists(path):
        print("File not found.")
        continue
    try:
        if path.endswith('.csv'):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
        
        chord_cols = [c for c in df.columns if 'lv_false_tendon' in c or 'chord' in c.lower() or 'ЛС ' in c]
        for c in chord_cols:
            nulls = df[c].isnull().sum()
            zeros = (df[c] == 0).sum()
            print(f"  {c}: {nulls} nulls, {zeros} zeros (Total: {len(df)})")
            
            # Print if any of them are missing 55 exactly
            if nulls == 55:
                print(f"  !!! BINGO: {c} has exactly 55 nulls !!!")
    except Exception as e:
        print(f"Error reading file: {e}")
