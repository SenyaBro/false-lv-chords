import pandas as pd
import os
import shutil

def main():
    old_file = r"data\final_analysis_dataset.xlsx"
    new_file = r"data\raw\final_analysis_dataset_Corr_08.05.2026.xlsx"
    backup_file = r"data\interim\final_analysis_dataset_backup.xlsx"
    
    # 1. Создаем бекап старого файла на всякий случай
    os.makedirs(r"data\interim", exist_ok=True)
    if os.path.exists(old_file):
        shutil.copy(old_file, backup_file)
        print(f"Backup saved to: {backup_file}")
    
    # 2. Загружаем данные
    print("Loading datasets...")
    df_old = pd.read_excel(old_file)
    df_new = pd.read_excel(new_file)
    
    # Нормализация ключа объединения
    if 'ФИО' in df_new.columns:
        df_new.rename(columns={'ФИО': 'subject_full_name'}, inplace=True)
    if 'ФИО' in df_old.columns:
        df_old.rename(columns={'ФИО': 'subject_full_name'}, inplace=True)
        
    # 3. Убедимся, что есть ключ для объединения
    merge_key = 'subject_full_name'
    if merge_key not in df_old.columns or merge_key not in df_new.columns:
        print(f"Error: Column '{merge_key}' not found in both datasets. Merge aborted.")
        return
        
    # 4. Выделяем нужные новые колонки на русском из сырого файла
    russian_cols = ['КДР', 'КСР', 'МЕТ', 'МПК']
    
    # Если эти колонки случайно добавились в прошлый раз, удалим их перед объединением
    existing_russian = [c for c in russian_cols if c in df_old.columns]
    if existing_russian:
        df_old.drop(columns=existing_russian, inplace=True)
        
    missing_cols = [c for c in russian_cols if c not in df_new.columns]
    if missing_cols:
        print(f"Error: Columns {missing_cols} not found in the new dataset.")
        return
        
    df_new_subset = df_new[[merge_key] + russian_cols].copy()
    
    # Сразу переименовываем их в канонические английские названия из словаря
    rename_dict = {
        'КДР': 'echo_lv_end_diastolic_diameter_mm',
        'КСР': 'echo_lv_end_systolic_diameter_mm',
        'МЕТ': 'exercise_metabolic_equivalent_mets',
        'МПК': 'exercise_vo2_max_ml_kg_min'
    }
    df_new_subset.rename(columns=rename_dict, inplace=True)
    
    # 5. Выполняем объединение (left join, чтобы сохранить все старые строки)
    # Если данные по ФИО могут дублироваться, нужно быть осторожным. 
    # В идеальном датасете ФИО уникальны.
    print(f"Rows before merge: {len(df_old)}")
    
    df_merged = pd.merge(df_old, df_new_subset, on=merge_key, how='left')
    
    print(f"Rows after merge: {len(df_merged)}")
    
    # Проверка на появление дубликатов из-за merge (если ФИО дублируются в df_new)
    if len(df_merged) > len(df_old):
        print("Warning: The number of rows increased after merge! Check for duplicated 'subject_full_name' in the new dataset.")
        
    # 6. Сохраняем обновленный файл
    # Мы сохраняем его в тот же файл (и у нас есть бекап)
    df_merged.to_excel(old_file, index=False)
    print(f"Successfully added columns: КДР, КСР, МЕТ, МПК")
    print(f"Updated dataset saved to: {old_file}")

if __name__ == "__main__":
    main()
