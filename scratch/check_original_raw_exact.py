import pandas as pd

raw_files = [
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\final_dataset_15_04.xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ИСХОДНЫЕ ДАННЫЕ 66 ЧЕЛОВЕК.xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ЭхоКГ и ЭКГ ОВЗ и здоровые 2026 (1).xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\набор данных для докторской диссертации 23_03_20.xls',
]

target_names = [
    "ЛС срединные косые",
    "ЛС срединные поперечные",
    "Поперечные срединные и базальные ЛС",
    "ЛС базальные косые",
    "ЛС базальные поперечные",
    "ЛС между срединным и базальным уровнями",
    "ЛС между срединным и апикальным уровнями",
    "ЛС между базальным и апикальным уровнями"
]

total_found = {k: 0 for k in target_names}

for f in raw_files:
    try:
        df = pd.read_excel(f)
        print(f"\n--- {f.split('\\')[-1]} (Rows: {len(df)}) ---")
        
        # We also want to check columns containing "ЛС" or "хорд" for potential matching
        found_any = False
        for col in df.columns:
            if not isinstance(col, str): continue
            
            clean_col = str(col).strip()
            if clean_col in target_names:
                non_null = df[col].notna().sum()
                zeros = (df[col] == 0).sum()
                print(f"  [EXACT MATCH] {clean_col}: {non_null} non-nulls (zeros: {zeros})")
                total_found[clean_col] += non_null
                found_any = True
            elif 'ЛС' in clean_col or 'хорд' in clean_col.lower():
                non_null = df[col].notna().sum()
                print(f"  [POTENTIAL] {clean_col}: {non_null} non-nulls")
                found_any = True
                
        if not found_any:
            print("  No related columns found.")
            
    except Exception as e:
        print(f"Error reading {f}: {e}")

print("\n=== SUMMARY ===")
for k, v in total_found.items():
    print(f"{k}: {v} total non-nulls in raw files")

