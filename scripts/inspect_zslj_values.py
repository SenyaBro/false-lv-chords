import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
dataset_path = PROJECT_ROOT / "data" / "final_analysis_dataset_ver2.xlsx"

df = pd.read_excel(dataset_path)

print(f"Dataset columns after execution: {list(df.columns[-5:])}")
target_col = "echo_lv_systolic_wall_stress_g_cm2"

if target_col in df.columns:
    print(f"\nSUCCESS: '{target_col}' found in dataset!")
    print(f"Non-null counts: {df[target_col].notna().sum()} / {len(df)}")
    print("\nDescriptive statistics:")
    print(df[target_col].describe())
    
    print("\nSample values with components:")
    sub_df = df[['subject_full_name', 'exercise_peak_systolic_bp_mmhg', 'echo_lv_end_systolic_diameter_mm', 'echo_lv_posterior_wall_thickness_mm', target_col]].dropna()
    print(sub_df.head(10))
else:
    print(f"\nERROR: '{target_col}' NOT found in dataset!")
