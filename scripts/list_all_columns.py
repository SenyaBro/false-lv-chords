import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_new.xlsx"

df = pd.read_excel(dataset_path)

print(f"Total rows: {len(df)}")
print("Columns and non-null counts:")
for c in df.columns:
    print(f"  {c}: {df[c].notna().sum()}")
