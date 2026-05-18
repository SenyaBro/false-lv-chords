import pandas as pd
import os

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

filtered_df = df[mask_all_zeros]

output_dir = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\interim"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "zero_chords_rows.xlsx")
filtered_df.to_excel(output_path, index=False)

print(f"Saved {len(filtered_df)} rows to {output_path}")
