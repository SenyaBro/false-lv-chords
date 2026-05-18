import pandas as pd
df_config = pd.read_excel(r'c:\Users\Ars\projects\university\lab_urfu_2026\table_const\config\dictional_filled_column_name.xlsx')
chords_mapping = df_config[df_config.apply(lambda row: row.astype(str).str.contains('lv_false_tendon|chord|хорд|Хорд', case=False).any(), axis=1)]
chords_mapping.to_csv(r'c:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\scratch\chords_mapping.csv', index=False, encoding='utf-8')
