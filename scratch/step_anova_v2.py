"""
Full Pipeline on ver2 dataset:
  1. Spatial Spread classification
  2. Levene + One-Way ANOVA (both DICOR targets)
  3. Effect sizes for dicor_sm_kdtr_cv_pct:
     η², Cohen's d, Hedges' g (Same Region vs Distant Regions)
"""

import os, warnings
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
             r"\false-lv-chords\data\final_analysis_dataset_ver2.xlsx")
OUT_DIR   = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\output\figures")
os.makedirs(OUT_DIR, exist_ok=True)

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
# ЗАГРУЗКА И КЛАССИФИКАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════
df_raw = pd.read_excel(DATA_PATH)
print(f"Датасет ver2: {df_raw.shape[0]} строк × {df_raw.shape[1]} колонок")

# Проверяем наличие нужных колонок
missing = [c for c in CHORD_COLS + TARGETS if c not in df_raw.columns]
if missing:
    print(f"⚠ Отсутствуют колонки: {missing}")
    # Попробуем найти похожие
    for m in missing:
        candidates = [c for c in df_raw.columns if m[:20] in c]
        print(f"  Кандидаты для '{m}': {candidates}")

df = df_raw.dropna(subset=TARGETS).copy()
print(f"После фильтрации по DICOR таргетам: n = {len(df)}")

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

print(f"\n── Распределение Chord_Spread_Class (ver2) ──")
for grp in GROUP_ORDER:
    n = (df["Chord_Spread_Class"] == grp).sum()
    print(f"  {grp:<22}: n = {n:>3}  ({100*n/len(df):.1f}%)")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 1. ТЕСТ ЛЕВЕНА
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "═"*70)
print("  ТЕСТ ЛЕВЕНА (Homogeneity of Variances) — ver2")
print("═"*70)

levene_results = {}
for target in TARGETS:
    groups_data = [
        df.loc[df["Chord_Spread_Class"] == g, target].dropna().values
        for g in valid_groups
    ]
    stat_l, p_l = stats.levene(*groups_data)
    levene_results[target] = {"stat": stat_l, "p": p_l}
    eq = "✓ равны" if p_l >= 0.05 else "✗ неравны"
    print(f"  {TARGET_LABELS[target].split(',')[0]:<45}  "
          f"W={stat_l:.4f}  p={p_l:.4f}  {eq}")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 2. ONE-WAY ANOVA
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "═"*70)
print("  ONE-WAY ANOVA — ver2")
print("═"*70)

anova_results = {}

for target in TARGETS:
    groups_data = [
        df.loc[df["Chord_Spread_Class"] == g, target].dropna().values
        for g in valid_groups
    ]
    F, p = stats.f_oneway(*groups_data)
    anova_results[target] = {"F": F, "p": p}

    sig = "✓ ЗНАЧИМО" if p < 0.05 else "✗ незначимо"
    print(f"\n  [{TARGET_LABELS[target].split(',')[0]}]")
    print(f"    {'Группа':<22}  {'n':>4}  {'Mean':>8}  {'SD':>8}  {'Median':>8}")
    print(f"    {'─'*58}")
    for g, gd in zip(valid_groups, groups_data):
        print(f"    {g:<22}  {len(gd):>4}  {np.mean(gd):>8.2f}  "
              f"{np.std(gd, ddof=1):>8.2f}  {np.median(gd):>8.2f}")
    print(f"\n    F = {F:.4f},  p = {p:.4f}  → {sig}")

    # Tukey HSD при p < 0.05
    if p < 0.05:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        all_vals   = df.loc[df["Chord_Spread_Class"].isin(valid_groups), target].dropna()
        all_groups = df.loc[all_vals.index, "Chord_Spread_Class"]
        tukey = pairwise_tukeyhsd(all_vals, all_groups, alpha=0.05)
        print(f"\n    Post-hoc Tukey HSD:")
        print(f"    {'Group 1':<22}  {'Group 2':<22}  {'Δ Mean':>8}  "
              f"{'p-adj':>8}  {'Sig':>6}")
        print(f"    {'─'*72}")
        for row in tukey.summary().data[1:]:
            g1, g2, meandiff, p_adj, lower, upper, reject = row
            print(f"    {str(g1):<22}  {str(g2):<22}  {meandiff:>+8.3f}  "
                  f"{p_adj:>8.4f}  {'***' if reject else 'n.s.':>6}")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 3. РАЗМЕРЫ ЭФФЕКТА для dicor_sm_kdtr_cv_pct
# ═══════════════════════════════════════════════════════════════════════════
TARGET_EFF = "dicor_sm_kdtr_cv_pct"

print("\n" + "═"*70)
print(f"  EFFECT SIZES — {TARGET_EFF}")
print("═"*70)

# ── η² (Eta-squared) ────────────────────────────────────────────────────────
groups_data_eff = [
    df.loc[df["Chord_Spread_Class"] == g, TARGET_EFF].dropna().values
    for g in valid_groups
]

# SS_between / SS_total
all_vals = np.concatenate(groups_data_eff)
grand_mean = np.mean(all_vals)
ss_total = np.sum((all_vals - grand_mean) ** 2)
ss_between = sum(len(gd) * (np.mean(gd) - grand_mean) ** 2 for gd in groups_data_eff)
ss_within = ss_total - ss_between

eta_sq = ss_between / ss_total

k = len(groups_data_eff)
N = len(all_vals)

# Partial η² (для one-way совпадает с η²)
partial_eta_sq = ss_between / (ss_between + ss_within)

# Omega-squared (менее предвзятая оценка)
df_between = k - 1
df_within  = N - k
ms_within  = ss_within / df_within
omega_sq   = (ss_between - df_between * ms_within) / (ss_total + ms_within)

# Интерпретация η²:  small ≈ 0.01, medium ≈ 0.06, large ≈ 0.14
if eta_sq < 0.01:   eta_label = "незначительный"
elif eta_sq < 0.06: eta_label = "малый (small)"
elif eta_sq < 0.14: eta_label = "средний (medium)"
else:               eta_label = "большой (large)"

print(f"\n  η² (Eta-squared)")
print(f"    SS_between = {ss_between:.3f}")
print(f"    SS_within  = {ss_within:.3f}")
print(f"    SS_total   = {ss_total:.3f}")
print(f"    η²         = {eta_sq:.4f}  ({eta_sq*100:.2f}%)")
print(f"    partial η²  = {partial_eta_sq:.4f}")
print(f"    ω² (omega)  = {omega_sq:.4f}")
print(f"    → Интерпретация: {eta_label}")

# ── Cohen's d и Hedges' g: Same Region vs Distant Regions ────────────────
g_same    = df.loc[df["Chord_Spread_Class"] == "Same Region",    TARGET_EFF].dropna().values
g_distant = df.loc[df["Chord_Spread_Class"] == "Distant Regions", TARGET_EFF].dropna().values

n1, n2 = len(g_same), len(g_distant)
m1, m2 = np.mean(g_same), np.mean(g_distant)
s1, s2 = np.std(g_same, ddof=1), np.std(g_distant, ddof=1)

# Cohen's d (pooled SD)
s_pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
cohen_d  = (m2 - m1) / s_pooled   # Distant - Same → положительный = Distant выше

# Hedges' g (корректировка для малых выборок)
# Correction factor J = 1 - 3 / (4*(n1+n2-2) - 1)
J = 1 - 3 / (4 * (n1 + n2 - 2) - 1)
hedges_g = cohen_d * J

# 95% CI для d (приближённая формула)
se_d = np.sqrt((n1 + n2) / (n1 * n2) + cohen_d**2 / (2 * (n1 + n2)))
ci_lo = cohen_d - 1.96 * se_d
ci_hi = cohen_d + 1.96 * se_d

# Интерпретация |d|:  small ≈ 0.2, medium ≈ 0.5, large ≈ 0.8
abs_d = abs(cohen_d)
if abs_d < 0.2:   d_label = "незначительный (<0.2)"
elif abs_d < 0.5: d_label = "малый (small, 0.2–0.5)"
elif abs_d < 0.8: d_label = "средний (medium, 0.5–0.8)"
else:             d_label = "большой (large, ≥0.8)"

print(f"\n  Cohen's d & Hedges' g  (Same Region vs Distant Regions)")
print(f"    Same Region:    n={n1},  M={m1:.2f},  SD={s1:.2f}")
print(f"    Distant Regions: n={n2},  M={m2:.2f},  SD={s2:.2f}")
print(f"    Pooled SD       = {s_pooled:.3f}")
print(f"    Δ Mean (Distant − Same) = {m2 - m1:+.3f}")
print(f"    Cohen's d       = {cohen_d:+.4f}  [95% CI: {ci_lo:+.4f}; {ci_hi:+.4f}]")
print(f"    Hedges' g       = {hedges_g:+.4f}")
print(f"    → Интерпретация: {d_label}")
print(f"    Положительный d означает: Distant Regions > Same Region")

# ── Дополнительно: d для Adjacent vs Same ────────────────────────────────
g_adj = df.loc[df["Chord_Spread_Class"] == "Adjacent Regions", TARGET_EFF].dropna().values
n_a = len(g_adj)
m_a = np.mean(g_adj)
s_a = np.std(g_adj, ddof=1)
s_p2 = np.sqrt(((n1 - 1) * s1**2 + (n_a - 1) * s_a**2) / (n1 + n_a - 2))
d_adj = (m_a - m1) / s_p2
J2 = 1 - 3 / (4 * (n1 + n_a - 2) - 1)
g_adj_h = d_adj * J2

print(f"\n  Дополнительно: Adjacent vs Same")
print(f"    Adjacent:  n={n_a},  M={m_a:.2f},  SD={s_a:.2f}")
print(f"    Cohen's d  = {d_adj:+.4f}")
print(f"    Hedges' g  = {g_adj_h:+.4f}")

# ── d для Distant vs Adjacent ────────────────────────────────────────────
s_p3 = np.sqrt(((n_a - 1) * s_a**2 + (n2 - 1) * s2**2) / (n_a + n2 - 2))
d_da = (m2 - m_a) / s_p3
J3 = 1 - 3 / (4 * (n_a + n2 - 2) - 1)
g_da = d_da * J3
print(f"\n  Дополнительно: Distant vs Adjacent")
print(f"    Cohen's d  = {d_da:+.4f}")
print(f"    Hedges' g  = {g_da:+.4f}")

print("\n" + "═"*70)

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 4. ВИЗУАЛИЗАЦИЯ (Q1-style)
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
    "dicor_ssou_cv_pct":    "anova_spread_ssou_v2.png",
    "dicor_sm_kdtr_cv_pct": "anova_spread_kdtr_v2.png",
}

df_plot = df[df["Chord_Spread_Class"].isin(valid_groups)].copy()

for target in TARGETS:
    fig, ax = plt.subplots(figsize=(5.5, 4.8))

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

    ax.set_xlabel("Chord Spatial Spread Class", fontsize=11, labelpad=9)
    ax.set_ylabel(TARGET_LABELS[target], fontsize=11, labelpad=9)
    ax.set_title("")

    F_val = anova_results[target]["F"]
    p_val = anova_results[target]["p"]
    p_str = f"p = {p_val:.3f}" if p_val >= 0.001 else "p < 0.001"
    ann = f"One-Way ANOVA\nF = {F_val:.2f}, {p_str}"

    # Добавляем η² для KDTR
    if target == TARGET_EFF:
        ann += f"\nη² = {eta_sq:.3f}"

    ax.text(0.97, 0.97, ann,
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=8.5, color="black", style="italic",
            multialignment="right",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="lightgrey", linewidth=0.7))

    xtick_labels = []
    for grp in valid_groups:
        sub = df_plot.loc[df_plot["Chord_Spread_Class"] == grp, target]
        xtick_labels.append(f"{grp}\n(n = {sub.count()})")
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

print("\n✓ Полный пайплайн на ver2 завершён.")
