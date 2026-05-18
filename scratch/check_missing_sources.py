import pandas as pd

df = pd.read_csv(r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\output\final_analysis_dataset.csv')

# The dataset has an origin/source column typically, e.g. "source_dataset" or "file_name"
source_cols = [c for c in df.columns if 'source' in c.lower() or 'file' in c.lower() or 'dataset' in c.lower()]
print("Potential source columns:", source_cols)

if source_cols:
    sc = source_cols[0]
    print(df.groupby(sc).size())
    
    # Check nulls for mid_obl per source
    if 'lv_false_tendon_mid_oblique_count' in df.columns:
        print("\nMissing values for 'lv_false_tendon_mid_oblique_count' by source:")
        for source, group in df.groupby(sc):
            missing = group['lv_false_tendon_mid_oblique_count'].isna().sum()
            total = len(group)
            print(f"  {source}: {missing} missing out of {total}")
            
