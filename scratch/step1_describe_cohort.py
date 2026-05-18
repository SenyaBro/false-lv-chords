"""
Шаг 1. Описание когорты для анализа echo_lv_strain_plus_cv_pct.
"""

import pandas as pd
import numpy as np

DATA_PATH = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_new.xlsx"

OUTCOME_COL     = "echo_lv_strain_plus_cv_pct"
PREDICTOR_COL   = "lv_false_tendon_total_count"
COVARIATE_COLS  = [
    "echo_lv_ejection_fraction_simpson_pct",
    "echo_lv_end_diastolic_volume_simpson_ml",
    "echo_lv_sphericity_index_end_diastolic_ratio",
]

PRETTY_NAMES = {
    "echo_lv_ejection_fraction_simpson_pct":           "EF (Simpson), %",
    "echo_lv_end_diastolic_volume_simpson_ml":         "EDV (Simpson), ml",
    "echo_lv_sphericity_index_end_diastolic_ratio":    "Sphericity Index (ED)",
}

# ── 1. Load ─────────────────────────────────────────────────────────────────
df_raw = pd.read_excel(DATA_PATH)
print(f"Исходный датасет: {df_raw.shape[0]} строк, {df_raw.shape[1]} колонок")

# ── 2. Check required columns ────────────────────────────────────────────────
required = [OUTCOME_COL, PREDICTOR_COL] + COVARIATE_COLS
missing_cols = [c for c in required if c not in df_raw.columns]
if missing_cols:
    raise ValueError(f"Отсутствуют колонки: {missing_cols}")

# ── 3. Filter: keep only rows with non-missing outcome ───────────────────────
df = df_raw.dropna(subset=[OUTCOME_COL]).copy()
print(f"\nПосле фильтрации по '{OUTCOME_COL}': {len(df)} пациентов")
print(f"  Исключено (нет outcome): {df_raw.shape[0] - len(df)}")

# ── 4. Chord count distribution ──────────────────────────────────────────────
print(f"\n── Распределение {PREDICTOR_COL} ──")
chord_counts = df[PREDICTOR_COL].value_counts(dropna=False).sort_index()
chord_missing = df[PREDICTOR_COL].isna().sum()

for val, n in chord_counts.items():
    label = "NaN" if pd.isna(val) else int(val)
    print(f"  {label:>4} хорд:  n = {n:>3}  ({100*n/len(df):.1f}%)")

if chord_missing:
    print(f"\n  ⚠ Пропуски в предикторе: {chord_missing} ({100*chord_missing/len(df):.1f}%)")

# ── 5. Missingness in covariates ─────────────────────────────────────────────
print(f"\n── Пропуски в ковариатах геометрии ──")
for col in COVARIATE_COLS:
    n_miss = df[col].isna().sum()
    print(f"  {PRETTY_NAMES[col]:<40} пропуски = {n_miss} ({100*n_miss/len(df):.1f}%)")

# ── 6. Descriptive stats (pre-standardization) ───────────────────────────────
print(f"\n── Дескриптивная статистика (до Z-стандартизации) ──")
desc = df[COVARIATE_COLS + [OUTCOME_COL]].describe().T[["count","mean","std","min","50%","max"]]
desc.index = [PRETTY_NAMES.get(i, i) for i in desc.index]
desc.columns = ["N","Mean","SD","Min","Median","Max"]
print(desc.round(2).to_string())

# ── 7. Z-standardise within this cohort ─────────────────────────────────────
for col in COVARIATE_COLS:
    z_col = col + "_z"
    df[z_col] = (df[col] - df[col].mean()) / df[col].std(ddof=1)

z_cols = [c + "_z" for c in COVARIATE_COLS]
print(f"\n── Проверка Z-стандартизации (mean ≈ 0, std ≈ 1) ──")
for col, zcol in zip(COVARIATE_COLS, z_cols):
    print(f"  {PRETTY_NAMES[col]:<40}  mean={df[zcol].mean():.4f}  std={df[zcol].std():.4f}")

print("\n✓ Шаг 1 завершён.")
