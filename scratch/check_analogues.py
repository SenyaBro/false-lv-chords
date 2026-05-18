import pandas as pd
import glob

config_path = r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\config\dictional_filled_column_name.xlsx'
df_config = pd.read_excel(config_path)

# Let's inspect columns of config
print("Columns in config:", df_config.columns.tolist())

# "Russian_Meaning", "Column_Name", "Analogue" are typically used
# I'll create a mapping from Target English Name -> list of alternative Russian names
mapping = {}
for idx, row in df_config.iterrows():
    col_name = str(row.get('Column_Name', ''))
    if 'lv_false_tendon' in col_name or 'count' in col_name:
        russian = str(row.get('Russian_Meaning', ''))
        analogue = str(row.get('Analogue', ''))
        
        alternatives = []
        if russian and russian != 'nan': alternatives.append(russian.strip())
        if analogue and analogue != 'nan': alternatives.append(analogue.strip())
        
        if alternatives:
            if col_name not in mapping:
                mapping[col_name] = set()
            mapping[col_name].update(alternatives)

for k, v in mapping.items():
    if 'oblique' in k or 'transverse' in k:
        print(f"Target: {k} => {v}")

raw_files = [
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\final_dataset_15_04.xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ИСХОДНЫЕ ДАННЫЕ 66 ЧЕЛОВЕК.xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ЭхоКГ и ЭКГ ОВЗ и здоровые 2026 (1).xlsx',
    r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\набор данных для докторской диссертации 23_03_20.xls',
]

for f in raw_files:
    try:
        df = pd.read_excel(f)
        fname = f.split('\\')[-1]
        print(f"\n--- {fname} (Rows: {len(df)}) ---")
        
        for k, alts in mapping.items():
            if 'oblique' not in k and 'transverse' not in k: continue
            
            for col in df.columns:
                if str(col).strip() in alts:
                    non_null = df[col].notna().sum()
                    print(f"  Found for {k}: column '{col}' has {non_null} non-nulls")
    except Exception as e:
        print(f"Error reading {f}: {e}")

