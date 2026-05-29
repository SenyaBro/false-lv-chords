import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
raw_path = PROJECT_ROOT / "data" / "raw" / "final_analysis_dataset_Corr_08.05.2026.xlsx"
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_new.xlsx"

df_raw = pd.read_excel(raw_path, sheet_name="Набор данных")
df_new = pd.read_excel(dataset_path)

print("Columns in df_new containing 'systolic' or 'pressure' or 'wall' or 'thickness' or 'diameter':")
kws = ["systolic", "pressure", "wall", "thickness", "diameter"]
for c in df_new.columns:
    if any(k in c.lower() for k in kws):
        print(f"  {c}")

print("\nSample values from df_new for:")
cols_to_print = [
    "exercise_peak_systolic_bp_mmhg",  # SAD max
    "echo_lv_end_systolic_diameter_mm",  # KSR
    "echo_lv_posterior_wall_thickness_mm" # ZS (diastolic)
]
for c in cols_to_print:
    if c in df_new.columns:
        print(f"  {c}: non-null count = {df_new[c].notna().sum()}, mean = {df_new[c].mean():.2f}, min = {df_new[c].min()}, max = {df_new[c].max()}")
    else:
        print(f"  {c} NOT FOUND in df_new!")

print("\nLet's check df_raw columns matching SAD, KSR, ZSLJ:")
for c in df_raw.columns:
    if "сад" in str(c).lower() or "кср" in str(c).lower() or "зс" in str(c).lower():
        print(f"  Raw column: {c}")
