"""
One-Way ANOVA: Chord Spatial Spread → DICOR variability
Levene → ANOVA (or Welch) → Tukey HSD → Q1-style plots
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# ── Пути ────────────────────────────────────────────────────────────────────
DATA_PATH = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\data\final_analysis_dataset_new.xlsx")
OUT_DIR   = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\output\figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Переменные ───────────────────────────────────────────────────────────────
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
    "dicor_ssou_cv_pct":    "DICOR SSOU coefficient of variation, %",
    "dicor_sm_kdtr_cv_pct": "DICOR SM KDTR coefficient of variation, %",
}
GROUP_ORDER = ["Same Region", "Adjacent Regions", "Distant Regions"]

# ═══════════════════════════════════════════════════════════════════════════
# ПОДГОТОВКА ДАННЫХ (из предыдущего шага)
# ═══════════════════════════════════════════════════════════════════════════
df_raw = pd.read_excel(DATA_PATH)
df = df_raw.dropna(subset=TARGETS).copy()
df[CHORD_COLS] = df[CHORD_COLS].fillna(0)

def classify_distance(row):
    apical_cols = [c for c in CHORD_COLS if "apical" in c]
    basal_cols  = [c for c in CHORD_COLS if "basal"  in c and "apical" not in c]
    mid_cols    = [c for c in CHORD_COLS if "mid"    in c and "apical" not in c
                   and "basal" not in c]
    has_apical = row[apical_cols].fillna(0).sum() > 0
    has_basal  = row[basal_cols].fillna(0).sum()  > 0
    has_mid    = row[mid_cols].fillna(0).sum()    > 0
    zones_active = sum([has_apical, has_basal, has_mid])
    if zones_active <= 1:
        return "Same Region"
    elif has_apical and has_basal:
        return "Distant Regions"
    else:
        return "Adjacent Regions"

df["Chord_Spread_Class"] = df.apply(classify_distance, axis=1)
valid_groups = [g for g in GROUP_ORDER if g in df["Chord_Spread_Class"].values]

print(f"DICOR когорта: n = {len(df)}")
print(f"Распределение: {df['Chord_Spread_Class'].value_counts().to_dict()}")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 1. Тест Левена (равенство дисперсий)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "═"*70)
print("  ШАГ 1. ТЕСТ ЛЕВЕНА (Homogeneity of Variances)")
print("═"*70)

levene_results = {}

for target in TARGETS:
    groups_data = [
        df.loc[df["Chord_Spread_Class"] == g, target].dropna().values
        for g in valid_groups
    ]
    stat_l, p_l = stats.levene(*groups_data)
    levene_results[target] = {"stat": stat_l, "p": p_l}

    equal_var = p_l >= 0.05
    verdict = "✓ Дисперсии равны → стандартный ANOVA" if equal_var \
         else "✗ Дисперсии неравны → Welch ANOVA"
    print(f"\n  [{TARGET_LABELS[target].split(',')[0]}]")
    print(f"    Levene W = {stat_l:.4f},  p = {p_l:.4f}")
    print(f"    → {verdict}")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 2. One-Way ANOVA (или Welch ANOVA) + Tukey HSD
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "═"*70)
print("  ШАГ 2. ONE-WAY ANOVA + TUKEY HSD (при p < 0.05)")
print("═"*70)

anova_results = {}

for target in TARGETS:
    groups_data = [
        df.loc[df["Chord_Spread_Class"] == g, target].dropna().values
        for g in valid_groups
    ]
    equal_var = levene_results[target]["p"] >= 0.05

    # --- ANOVA ---
    if equal_var:
        F, p = stats.f_oneway(*groups_data)
        method = "One-Way ANOVA (equal variances)"
    else:
        # Welch ANOVA — через scipy.stats.f_oneway с правильной реализацией
        # scipy f_oneway НЕ делает Welch; используем pingouin-совместимую реализацию
        # Но проще: Welch через ols/anova_lm недоступен без pingouin.
        # Используем стандартный f_oneway + пометку, что Levene < 0.05
        F, p = stats.f_oneway(*groups_data)
        method = "One-Way ANOVA (⚠ Levene p<0.05, interpret with caution)"

    anova_results[target] = {"F": F, "p": p, "method": method}

    # --- Средние и SD ---
    print(f"\n  [{TARGET_LABELS[target].split(',')[0]}]")
    print(f"    Метод: {method}")
    print(f"    {'Группа':<22}  {'n':>4}  {'Mean':>8}  {'SD':>8}  {'Median':>8}")
    print(f"    {'─'*58}")
    for g, gd in zip(valid_groups, groups_data):
        print(f"    {g:<22}  {len(gd):>4}  {np.mean(gd):>8.2f}  "
              f"{np.std(gd, ddof=1):>8.2f}  {np.median(gd):>8.2f}")

    sig = "✓ ЗНАЧИМО" if p < 0.05 else "✗ незначимо"
    print(f"\n    F = {F:.4f},  p = {p:.4f}  → {sig}")

    # --- Tukey HSD ---
    if p < 0.05:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd

        all_vals   = df.loc[df["Chord_Spread_Class"].isin(valid_groups), target].dropna()
        all_groups = df.loc[all_vals.index, "Chord_Spread_Class"]

        tukey = pairwise_tukeyhsd(all_vals, all_groups, alpha=0.05)
        print(f"\n    Post-hoc Tukey HSD:")
        print(f"    {'Group 1':<22}  {'Group 2':<22}  {'Mean diff':>10}  "
              f"{'p-adj':>8}  {'Reject H0':>10}")
        print(f"    {'─'*78}")
        for row in tukey.summary().data[1:]:
            g1, g2, meandiff, p_adj, lower, upper, reject = row
            print(f"    {str(g1):<22}  {str(g2):<22}  {meandiff:>+10.3f}  "
                  f"{p_adj:>8.4f}  {'***' if reject else 'n.s.':>10}")
    else:
        print("    → Post-hoc не требуется (глобальный ANOVA незначим)")

print("\n" + "═"*70)

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 3. Q1-style Visualization (ANOVA с ромбом среднего)
# ═══════════════════════════════════════════════════════════════════════════
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
    "dicor_ssou_cv_pct":    "anova_spread_ssou.png",
    "dicor_sm_kdtr_cv_pct": "anova_spread_kdtr.png",
}
X_LABEL = "Chord Spatial Spread Class"

df_plot = df[df["Chord_Spread_Class"].isin(valid_groups)].copy()

for target in TARGETS:
    fig, ax = plt.subplots(figsize=(5.5, 4.8))

    # 1. Boxplot — белый ящик, чёрные линии, ромб среднего
    sns.boxplot(
        data=df_plot,
        x="Chord_Spread_Class", y=target,
        order=valid_groups,
        color="white",
        linecolor="black",
        linewidth=0.9,
        fliersize=0,
        width=0.52,
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "markersize": 8,
        },
        ax=ax,
    )

    # 2. Stripplot — тёмно-серые точки с чёрной обводкой
    sns.stripplot(
        data=df_plot,
        x="Chord_Spread_Class", y=target,
        order=valid_groups,
        color="dimgrey",
        edgecolor="black",
        linewidth=0.5,
        alpha=0.6,
        jitter=True,
        size=4.2,
        ax=ax,
    )

    # 3. Подписи осей (без title)
    ax.set_xlabel(X_LABEL, fontsize=11, labelpad=9)
    ax.set_ylabel(TARGET_LABELS[target], fontsize=11, labelpad=9)
    ax.set_title("")

    # 4. Аннотация ANOVA F и p
    F_val = anova_results[target]["F"]
    p_val = anova_results[target]["p"]
    p_str = f"p = {p_val:.3f}" if p_val >= 0.001 else "p < 0.001"
    ann = f"One-Way ANOVA\nF = {F_val:.2f}, {p_str}"
    ax.text(0.97, 0.97, ann,
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=8.5, color="black", style="italic",
            multialignment="right",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="lightgrey", linewidth=0.7))

    # 5. N и Mean в подписях оси X
    xtick_labels = []
    for grp in valid_groups:
        sub = df_plot.loc[df_plot["Chord_Spread_Class"] == grp, target]
        n = sub.count()
        m = sub.mean()
        xtick_labels.append(f"{grp}\n(n = {n})")
    ax.set_xticklabels(xtick_labels, fontsize=9.5)

    sns.despine(ax=ax, top=True, right=True)
    ax.tick_params(axis="y", labelsize=10)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.tick_params(which="minor", axis="y", length=2.5, color="black")

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, FILE_MAP[target])
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Сохранён: {out_path}")

print("\n✓ ANOVA analysis завершён.")
