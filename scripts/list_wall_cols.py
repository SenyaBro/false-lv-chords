import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_new.xlsx"
df = pd.read_excel(dataset_path)

print(f"Total rows in dataset: {len(df)}")
kws = ["thickness", "wall", "septum", "зс", "тзс", "мжп", "задн", "систол", "диаметр", "кср", "кдр", "bp", "сад", "дад", "давл"]
matched = []
for c in df.columns:
    if any(k in str(c).lower() for k in kws):
        matched.append(c)

print(f"Matched columns ({len(matched)}):")
for m in matched:
    print(f"  {m}: non-null count = {df[m].notna().sum()}, sample = {list(df[m].dropna().head())}")
