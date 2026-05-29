import pandas as pd
import re
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")

# 1. Search columns in the dataset
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_new.xlsx"
df = pd.read_excel(dataset_path)

columns = list(df.columns)
print(f"Total columns in dataset: {len(columns)}")

# We look for keywords:
# P: "давление", "давл", "систолическое", "bp", "sbp", "pressure", "ad", "ад"
# d: "кср", "esd", "diameter", "end_systolic", "ксд", "esv"
# h: "тзс", "зс", "задн", "стена", "стенк", "систол", "posterior", "wall", "thickness", "lvpws"

p_keywords = ["давление", "давл", "систолическое", "bp", "sbp", "pressure", "ad", "ад"]
d_keywords = ["кср", "esd", "diameter", "end_systolic", "ксд"]
h_keywords = ["тзс", "зс", "задн", "стена", "стенк", "систол", "posterior", "wall", "thickness", "lvpws", "тзслжс"]

matched_p = [c for c in columns if any(k in c.lower() for k in p_keywords)]
matched_d = [c for c in columns if any(k in c.lower() for k in d_keywords)]
matched_h = [c for c in columns if any(k in c.lower() for k in h_keywords)]

print("\n--- Candidate columns for P (pressure) ---")
for col in matched_p:
    print(f"  {col}")

print("\n--- Candidate columns for d (КСР) ---")
for col in matched_d:
    print(f"  {col}")

print("\n--- Candidate columns for h (ТЗСлжс) ---")
for col in matched_h:
    print(f"  {col}")
