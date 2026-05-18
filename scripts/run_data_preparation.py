import pandas as pd
import numpy as np
import os
import sys
from sklearn.impute import KNNImputer

# Убедимся, что мы можем импортировать из src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fh_res.data.dictionary_parser import load_variable_mapping

def main():
    dataset_path = r"data\final_analysis_dataset.xlsx"
    dict_path = r"docs\VARIABLE_DICTIONARY.md"
    output_path = r"data\interim\eda_dataset_imputed.csv"
    
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found.")
        return
        
    print("1. Loading raw dataset and parsing dictionary...")
    df = pd.read_excel(dataset_path)
    rename_map, var_meta = load_variable_mapping(dict_path)
    
    # Сначала найдем колонку ФИО/name и убедимся, что она переименуется в subject_full_name
    if 'name' in df.columns and 'name' not in rename_map:
        rename_map['name'] = 'subject_full_name'
    if 'ФИО' in df.columns and 'ФИО' not in rename_map:
        rename_map['ФИО'] = 'subject_full_name'
        
    df = df.rename(columns=rename_map)
    
    # Оставим только те колонки, которые есть в словаре (или переименовались)
    # Это важно, чтобы избавиться от старого мусора, если он был.
    # Но чтобы не потерять данные случайно, просто работаем со всеми текущими.
    
    # 2. Детерминированное восстановление
    print("\n2. Applying deterministic imputation...")
    
    # 2.1 ОВЗ (special_health_needs_flag)
    if 'special_health_needs_flag' in df.columns:
        # Приводим к строке, убираем пробелы, чтобы отловить пустые строки
        s = df['special_health_needs_flag'].astype(str).str.strip().str.lower()
        # NaN в pandas при astype(str) становится 'nan'
        empty_vals = ['nan', 'none', '', '0', '0.0']
        
        # Если значение пустое или 0 -> 0, иначе 1
        df['special_health_needs_flag'] = s.apply(lambda x: 0 if x in empty_vals else 1)
        print(" - Converted 'special_health_needs_flag' to binary (0/1).")

    # 2.2 BMI
    if 'weight_kg' in df.columns and 'height_cm' in df.columns:
        if 'body_mass_index_kg_m2' not in df.columns:
            df['body_mass_index_kg_m2'] = np.nan
        bmi_mask = df['body_mass_index_kg_m2'].isna() & df['weight_kg'].notna() & df['height_cm'].notna()
        df.loc[bmi_mask, 'body_mass_index_kg_m2'] = df.loc[bmi_mask, 'weight_kg'] / ((df.loc[bmi_mask, 'height_cm'] / 100) ** 2)
        print(f" - Calculated BMI for {bmi_mask.sum()} missing rows.")
        
    # 2.3 BSA (Du Bois)
    if 'weight_kg' in df.columns and 'height_cm' in df.columns:
        if 'body_surface_area_m2' not in df.columns:
            df['body_surface_area_m2'] = np.nan
        bsa_mask = df['body_surface_area_m2'].isna() & df['weight_kg'].notna() & df['height_cm'].notna()
        df.loc[bsa_mask, 'body_surface_area_m2'] = 0.007184 * (df.loc[bsa_mask, 'height_cm'] ** 0.725) * (df.loc[bsa_mask, 'weight_kg'] ** 0.425)
        print(f" - Calculated BSA for {bsa_mask.sum()} missing rows.")
        
    # 2.4 Total chord count
    # Ищем все колонки хорд, которые заканчиваются на oblique_count или transverse_count
    # Это сегментарные хорды.
    if 'lv_false_tendon_total_count' not in df.columns:
        df['lv_false_tendon_total_count'] = np.nan
        
    count_mask = df['lv_false_tendon_total_count'].isna()
    segment_cols = [c for c in df.columns if c.startswith('lv_false_tendon_') and 
                    (c.endswith('_oblique_count') or c.endswith('_transverse_count'))]
    
    if segment_cols:
        # Суммируем сегменты и делим на 2
        df.loc[count_mask, 'lv_false_tendon_total_count'] = df.loc[count_mask, segment_cols].sum(axis=1) / 2
        print(f" - Calculated total chord count for {count_mask.sum()} missing rows.")

    # 3. Умное заполнение (Smart Imputation) с помощью KNN
    print("\n3. Performing smart imputation (KNN)...")
    
    # Ключевые слова для ЗАПРЕЩЕННЫХ колонок (исходы, фенотип хорд, пол, идентификаторы)
    # Важно: EF (ejection_fraction) запрещено, но geometry (diameter, volume) разрешено!
    restricted_keywords = [
        'strain', 
        'dicor', 
        'ecg', 
        'ejection_fraction', 
        'sex', 
        'tendon', 
        'chord', 
        'special_health_needs_flag', 
        'subject_full_name'
    ]
    
    restricted_cols = [c for c in df.columns if any(k in c for k in restricted_keywords)]
    allowed_cols = [c for c in df.columns if c not in restricted_cols]
    
    # Приводим allowed_cols к числовому типу, если там затесался текст (например, опечатки '12,5' вместо '12.5')
    for col in allowed_cols:
        if df[col].dtype == object:
            # Пробуем заменить запятые на точки и конвертировать
            df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Убираем колонки, которые полностью состоят из NaN (их невозможно импутировать)
    allowed_cols = [c for c in allowed_cols if not df[c].isna().all()]
            
    print(f" - Imputing {len(allowed_cols)} allowed columns (KNN, 5 neighbors)...")
    print(f" - Skipping {len(restricted_cols)} restricted columns...")
    
    imputer = KNNImputer(n_neighbors=5)
    
    # Сохраняем исходные значения, чтобы проверить, что изменилось (опционально)
    imputed_data = imputer.fit_transform(df[allowed_cols])
    
    # Обновляем датафрейм
    df[allowed_cols] = imputed_data
    
    # 4. Сохранение
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n4. Success! Imputed EDA dataset saved to {output_path}")
    print(f"Dataset shape: {df.shape}")

if __name__ == "__main__":
    main()
