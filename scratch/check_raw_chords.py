import pandas as pd
import os
import glob

raw_dir = r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\data'
all_files = glob.glob(raw_dir + '/**/*.csv', recursive=True)

# Find raw data files, e.g. the 4 raw tables
raw_tables = [f for f in all_files if 'raw_tables' in f and 'combined' in f.lower() and 'v4' in f]
raw_tables.extend([f for f in all_files if 'raw_tables' in f and 'combined' in f.lower() and 'v1' in f])

print(f"Found {len(raw_tables)} possible raw combined tables.")
for p in raw_tables[:3]:
    print(f"Reading {p}")
    try:
        df = pd.read_csv(p, low_memory=False)
        # Search for columns that might relate to chords
        cols = [c for c in df.columns if isinstance(c, str) and ('ЛС' in c or 'хорд' in c.lower() or 'chord' in c.lower() or 'mid' in c.lower() or 'obl' in c.lower() or 'trans' in c.lower())]
        print("Related columns:", cols)
        for c in cols:
            non_null = df[c].notna().sum()
            print(f"  {c}: {non_null} non-nulls (Total: {len(df)})")
    except Exception as e:
        print(f"Error: {e}")
