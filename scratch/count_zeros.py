import pandas as pd
import sys

file_path = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_old.xlsx"
df = pd.read_excel(file_path)

cols = [
    'lv_false_tendon_mid_oblique_count',
    'lv_false_tendon_mid_transverse_count',
    'lv_false_tendon_mid_and_basal_transverse_count',
    'lv_false_tendon_basal_oblique_count',
    'lv_false_tendon_basal_transverse_count',
    'lv_false_tendon_mid_to_basal_oblique_count',
    'lv_false_tendon_mid_to_apical_oblique_count',
    'lv_false_tendon_basal_to_apical_oblique_count'
]

subset = df[cols].fillna(0)
mask_all_zeros = (subset == 0).all(axis=1)

print(f"Total: {len(df)}")
print(f"All zeros (no values): {mask_all_zeros.sum()}")
print(f"At least one non-zero: {(~mask_all_zeros).sum()}")
