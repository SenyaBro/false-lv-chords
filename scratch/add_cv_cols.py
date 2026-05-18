import pandas as pd
import numpy as np

# Read the file we just created
input_path = 'data/final_analysis_dataset_with_cv.xlsx'
df = pd.read_excel(input_path)

# Find dicor columns
sm_kdtr_cols = [c for c in df.columns if 'dicor_sm_kdtr_' in c and c.endswith('_mm')]
ssou_cols = [c for c in df.columns if 'dicor_ssou_' in c and c.endswith('_pct')]

print(f"Found {len(sm_kdtr_cols)} dicor_sm_kdtr columns.")
print(f"Found {len(ssou_cols)} dicor_ssou columns.")

# Calculate CV
df['dicor_sm_kdtr_cv_pct'] = (df[sm_kdtr_cols].std(axis=1) / df[sm_kdtr_cols].mean(axis=1)) * 100
df['dicor_ssou_cv_pct'] = (df[ssou_cols].std(axis=1) / df[ssou_cols].mean(axis=1)) * 100

print(df[['dicor_sm_kdtr_cv_pct', 'dicor_ssou_cv_pct']].head())

# Save back to the file
output_path = 'data/final_analysis_dataset_with_cv.xlsx'
df.to_excel(output_path, index=False)
print(f"Saved successfully to {output_path}.")
