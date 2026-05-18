import pandas as pd
import glob
import re

raw_files = [
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\final_dataset_15_04.xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ИСХОДНЫЕ ДАННЫЕ 66 ЧЕЛОВЕК.xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ЭхоКГ и ЭКГ ОВЗ и здоровые 2026 (1).xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\набор данных для докторской диссертации 23_03_20.xls',
]

def find_chords(df, name):
    print(f"\n--- {name} (Rows: {len(df)}) ---")
    chord_cols = [c for c in df.columns if isinstance(c, str) and bool(re.search(r'ЛС|хорд|chord|ЛЖ', c, re.IGNORECASE))]
    if not chord_cols:
        print("No chord columns found")
        return
    for c in chord_cols:
        non_null = df[c].notna().sum()
        if non_null > 0:
            print(f"  {c}: {non_null} non-nulls")

for f in raw_files:
    try:
        df = pd.read_excel(f)
        find_chords(df, f.split('\\')[-1])
    except Exception as e:
        print(f"Error reading {f}: {e}")
