"""
Topology-based Feature Engineering + Kruskal-Wallis + Q1-style Visualization
Target cohort: DICOR patients
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# ── Пути ────────────────────────────────────────────────────────────────────
DATA_PATH = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\data\final_analysis_dataset_new.xlsx")
OUT_DIR   = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\output\figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Колонки хорд для классификации ──────────────────────────────────────────
CHORD_COLS = [
    "lv_false_tendon_mid_oblique_count",
    "lv_false_tendon_mid_transverse_count",
    "lv_false_tendon_mid_and_basal_transverse_count",
    "lv_false_tendon_basal_oblique_count",
    "lv_false_tendon_basal_transverse_count",
    "lv_false_tendon_mid_to_basal_oblique_count",
    "lv_false_tendon_mid_to_apical_oblique_count",
    "lv_false_tendon_basal_to_apical_oblique_count",
]

TARGETS = ["dicor_ssou_cv_pct", "dicor_sm_kdtr_cv_pct"]

TARGET_LABELS = {
    "dicor_ssou_cv_pct":    "DICOR SSOU CV, %",
    "dicor_sm_kdtr_cv_pct": "DICOR SM KDTR CV, %",
}

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 1. Feature Engineering
# ═══════════════════════════════════════════════════════════════════════════
df_raw = pd.read_excel(DATA_PATH)
print(f"Исходный датасет: {df_raw.shape[0]} × {df_raw.shape[1]}")

# Фильтр по наличию обоих DICOR-таргетов
df = df_raw.dropna(subset=TARGETS).copy()
print(f"После фильтрации по DICOR таргетам: n = {len(df)}")

# Заполняем пропуски в CHORD_COLS нулями (отсутствие типа = 0 хорд)
df[CHORD_COLS] = df[CHORD_COLS].fillna(0)

# ── Классификация ────────────────────────────────────────────────────────────
def classify_topology_complex(row):
    # 1. Определяем колонки для каждой зоны (как вы и написали)
    apical_cols = [c for c in CHORD_COLS if "apical" in c]
    basal_cols  = [c for c in CHORD_COLS if "basal"  in c and "apical" not in c]
    mid_cols    = [c for c in CHORD_COLS if "mid"    in c and "apical" not in c and "basal" not in c]

    # 2. Проверяем наличие хорд в каждой из зон (добавлено fillna(0) для защиты от NaN)
    has_apical = row[apical_cols].fillna(0).sum() > 0
    has_basal  = row[basal_cols].fillna(0).sum()  > 0
    has_mid    = row[mid_cols].fillna(0).sum()    > 0

    # 3. Считаем, сколько независимых зон задето
    zones_active = sum([has_apical, has_basal, has_mid])

    # 4. Логика ветвления
    if zones_active > 1:
        # У пациента есть независимые хорды в РАЗНЫХ зонах 
        # (например, >0 в apical_cols И >0 в mid_cols)
        return "Complex / Multi-zone"
    elif has_apical:
        return "Apical-Involved"
    elif has_basal:
        return "Basal-Involved"
    elif has_mid:
        return "Mid-Only"
    else:
        return "Unclassified"

# Применяем к датасету
df["Chord_Topology_Class"] = df.apply(classify_topology_complex, axis=1)

# ── Таблица частот ───────────────────────────────────────────────────────────
freq = df["Chord_Topology_Class"].value_counts()
print("\n── Распределение Chord_Topology_Class ──")
for cls, n in freq.items():
    print(f"  {cls:<22}: n = {n:>3}  ({100*n/len(df):.1f}%)")

# Удалим неклассифицированных (если есть)
n_unclass = (df["Chord_Topology_Class"] == "Unclassified").sum()
if n_unclass > 0:
    print(f"\n  ⚠ Unclassified: {n_unclass} — исключены из анализа")
    df = df[df["Chord_Topology_Class"] != "Unclassified"].copy()
    print(f"  Рабочая выборка: n = {len(df)}")

# Порядок групп для отображения
GROUP_ORDER = ["Apical-Involved", "Basal-Involved", "Mid-Only"]

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 2. Kruskal-Wallis + Dunn's post-hoc
# ═══════════════════════════════════════════════════════════════════════════

def dunn_bonferroni(df, group_col, value_col, groups):
    """
    Dunn's test вручную: попарные ранговые тесты Манна-Уитни
    с поправкой Бонферрони.
    """
    from itertools import combinations
    pairs = list(combinations(groups, 2))
    k = len(pairs)
    rows = []
    for g1, g2 in pairs:
        x1 = df.loc[df[group_col] == g1, value_col].dropna()
        x2 = df.loc[df[group_col] == g2, value_col].dropna()
        _, p_raw = stats.mannwhitneyu(x1, x2, alternative="two-sided")
        p_adj = min(p_raw * k, 1.0)   # Bonferroni
        rows.append({
            "Group 1": g1, "Group 2": g2,
            "U-stat": _,
            "p (raw)": p_raw,
            "p (Bonferroni)": p_adj,
        })
    return pd.DataFrame(rows)


print("\n" + "═"*68)
print("  ТЕСТ КРАСКЕЛА-УОЛЛИСА + POST-HOC ДАННА (поправка Бонферрони)")
print("═"*68)

kw_results = {}

for target in TARGETS:
    groups_data = [
        df.loc[df["Chord_Topology_Class"] == g, target].dropna().values
        for g in GROUP_ORDER
        if g in df["Chord_Topology_Class"].values
    ]
    valid_groups = [g for g in GROUP_ORDER if g in df["Chord_Topology_Class"].values]

    H, p = stats.kruskal(*groups_data)
    kw_results[target] = {"H": H, "p": p}

    sig = "✓ ЗНАЧИМО" if p < 0.05 else "✗ незначимо"
    print(f"\n  [{TARGET_LABELS[target]}]")
    print(f"    Kruskal-Wallis H = {H:.4f},  p = {p:.4f}  → {sig}")

    # Медианы по группам
    print(f"    Медианы:")
    for g, gd in zip(valid_groups, groups_data):
        print(f"      {g:<22}: median = {np.median(gd):.2f}  (n={len(gd)})")

    if p < 0.05:
        print(f"\n    Post-hoc Dunn (Bonferroni):")
        ph = dunn_bonferroni(df, "Chord_Topology_Class", target, valid_groups)
        for _, row in ph.iterrows():
            sig_ph = "* p<0.05" if row["p (Bonferroni)"] < 0.05 else "n.s."
            print(f"      {row['Group 1']} vs {row['Group 2']}: "
                  f"p_raw={row['p (raw)']:.4f}  p_adj={row['p (Bonferroni)']:.4f}  {sig_ph}")

print("\n" + "═"*68)

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 3. Q1-Style Visualization
# ═══════════════════════════════════════════════════════════════════════════

# Стиль, строго соответствующий требованиям пользователя
plt.style.use("default")
sns.set_theme(style="ticks", context="paper", font_scale=1.2)
plt.rcParams.update({
    "figure.facecolor":  "white",
    "axes.facecolor":    "white",
    "text.color":        "black",
    "axes.labelcolor":   "black",
    "xtick.color":       "black",
    "ytick.color":       "black",
    "axes.edgecolor":    "black",
    "font.family":       "sans-serif",
    "font.sans-serif":   ["Arial", "DejaVu Sans"],
    "axes.linewidth":    0.9,
    "xtick.major.width": 0.9,
    "ytick.major.width": 0.9,
})

FILE_MAP = {
    "dicor_ssou_cv_pct":    "topology_vs_ssou.png",
    "dicor_sm_kdtr_cv_pct": "topology_vs_kdtr.png",
}

X_LABEL = "Chord Topology Class"

Y_LABELS = {
    "dicor_ssou_cv_pct":    "DICOR SSOU coefficient of variation, %",
    "dicor_sm_kdtr_cv_pct": "DICOR SM KDTR coefficient of variation, %",
}

for target in TARGETS:
    fig, ax = plt.subplots(figsize=(5.2, 4.6))

    present_groups = [g for g in GROUP_ORDER
                      if g in df["Chord_Topology_Class"].values]

    # 1. Boxplot — белая заливка, чёрные линии
    sns.boxplot(
        data=df[df["Chord_Topology_Class"].isin(present_groups)],
        x="Chord_Topology_Class", y=target,
        order=present_groups,
        color="white",
        linecolor="black",
        linewidth=0.9,
        fliersize=0,          # выбросы скроем — покажем их через stripplot
        width=0.5,
        ax=ax,
    )

    # 2. Stripplot — тёмно-серые точки, чёрная обводка
    sns.stripplot(
        data=df[df["Chord_Topology_Class"].isin(present_groups)],
        x="Chord_Topology_Class", y=target,
        order=present_groups,
        color="dimgrey",
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7,
        jitter=True,
        size=4.0,
        ax=ax,
    )

    # 3. Подписи осей (без заголовка)
    ax.set_xlabel(X_LABEL, fontsize=11, labelpad=8)
    ax.set_ylabel(Y_LABELS[target], fontsize=11, labelpad=8)
    ax.set_title("")     # явно убираем заголовок

    # 4. Аннотация H и p Краскела-Уоллиса в правом верхнем углу
    H_val = kw_results[target]["H"]
    p_val = kw_results[target]["p"]
    p_str = f"p = {p_val:.3f}" if p_val >= 0.001 else "p < 0.001"
    kw_str = f"Kruskal-Wallis H = {H_val:.2f}, {p_str}"
    ax.text(0.98, 0.98, kw_str,
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=8.5, color="black",
            style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="lightgrey", linewidth=0.7))

    # 5. Финальный вид
    sns.despine(ax=ax, top=True, right=True)
    ax.tick_params(axis="x", labelsize=10, rotation=12)
    ax.tick_params(axis="y", labelsize=10)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.tick_params(which="minor", axis="y", length=2.5, color="black")

    plt.tight_layout()

    out_path = os.path.join(OUT_DIR, FILE_MAP[target])
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Сохранён: {out_path}")

print("\n✓ Topology analysis завершён.")
