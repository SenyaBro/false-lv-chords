import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
raw_path = PROJECT_ROOT / "data" / "raw" / "final_analysis_dataset_Corr_08.05.2026.xlsx"

# Let's read all sheet names and their columns
xl = pd.ExcelFile(raw_path)
for sheet in xl.sheet_names:
    print(f"\nSheet: {sheet}")
    df = xl.parse(sheet, nrows=5)
    cols = list(df.columns)
    print(f"Total columns: {len(cols)}")
    
    # Search for any wall thickness, pressure, diameter keywords
    kws = ["задн", "толщ", "зс", "тзс", "давл", "сад", "дад", "кср", "кдр", "систол", "pressure", "bp", "esd", "diameter", "thickness", "wall"]
    matched = [c for c in cols if any(kw in str(c).lower() for kw in kws)]
    print(f"Matched columns ({len(matched)}):")
    for m in matched:
        # Check if it has non-null values in the first 5 rows
        print(f"  {m}")
