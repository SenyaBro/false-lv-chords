import pandas as pd
import re
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_new.xlsx"
df = pd.read_excel(dataset_path)
columns = list(df.columns)

print("--- ALL COLUMNS CONTAINING 'bp', 'ad', 'sist', 'sys', 'press', 'давл', 'сис', 'сд', 'ад' ---")
patterns = ["bp", "ad", "sist", "sys", "press", "давл", "сис", "сд", "ад"]
for col in columns:
    col_lower = col.lower()
    if any(pat in col_lower for pat in patterns):
        print(f"  {col}")

print("\n--- ALL COLUMNS CONTAINING 'thickness', 'wall', 'septum', 'зс', 'тзс', 'мжп', 'posterior' ---")
patterns_h = ["thickness", "wall", "septum", "зс", "тзс", "мжп", "posterior"]
for col in columns:
    col_lower = col.lower()
    if any(pat in col_lower for pat in patterns_h):
        print(f"  {col}")

print("\n--- ALL COLUMNS CONTAINING 'diameter', 'кср', 'esd', 'систол' ---")
patterns_d = ["diameter", "кср", "esd", "систол"]
for col in columns:
    col_lower = col.lower()
    if any(pat in col_lower for pat in patterns_d):
        print(f"  {col}")
