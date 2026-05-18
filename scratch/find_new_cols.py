import pandas as pd

old_file = r"data\final_analysis_dataset.xlsx"
new_file = r"data\raw\final_analysis_dataset_Corr_08.05.2026.xlsx"

try:
    df_old = pd.read_excel(old_file)
    old_cols = list(df_old.columns)
except Exception as e:
    print(f"Error reading {old_file}: {e}")
    old_cols = []

try:
    df_new = pd.read_excel(new_file)
    new_cols = list(df_new.columns)
except Exception as e:
    print(f"Error reading {new_file}: {e}")
    new_cols = []

new_in_new = [c for c in new_cols if c not in old_cols]
print("New columns:")
for c in new_in_new:
    print(f"- {c}")
