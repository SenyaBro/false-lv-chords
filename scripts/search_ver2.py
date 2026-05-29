import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_ver2.xlsx"
dict_path = PROJECT_ROOT / "docs" / "VARIABLE_DICTIONARY.md"

df = pd.read_excel(dataset_path)
columns = list(df.columns)
print(f"Total rows in ver2: {len(df)}")
print(f"Total columns in ver2: {len(columns)}")

# Let's search columns that contain:
# ЗС, САС, САД, нагрузки, КСР
# Let's search in the dictionary and print rows that match
dict_content = dict_path.read_text(encoding="utf-8")

print("\n--- Search columns in ver2 ---")
kws = ["зс", "сад", "сас", "нагрузк", "кср", "задн", "толщ", "diameter", "thickness", "pressure", "bp", "peak"]
for col in columns:
    col_lower = str(col).lower()
    if any(k in col_lower for k in kws):
        # Print column and non-null count
        print(f"  {col}: non-null count = {df[col].notna().sum()}, sample = {list(df[col].dropna().head(3))}")

print("\n--- Search dictionary matching rows ---")
for line in dict_content.splitlines():
    line_lower = line.lower()
    if any(k in line_lower for k in ["зс", "сад", "сас", "нагрузки", "кср"]):
        print(line)
