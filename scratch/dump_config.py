import pandas as pd

# Load the config
config_path = r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\config\dictional_filled_column_name.xlsx'
df_config = pd.read_excel(config_path)

# Filter rows where target column might contain "lv_false_tendon" or "chord"
chords_mapping = df_config[df_config.apply(lambda row: row.astype(str).str.contains('lv_false_tendon|chord|хорд|Хорд', case=False).any(), axis=1)]

print(chords_mapping)
