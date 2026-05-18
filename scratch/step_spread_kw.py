"""
Spatial Spread Classification + Kruskal-Wallis + Q1-style Visualization
Target cohort: DICOR patients
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# ── Пути ────────────────────────────────────────────────────────────────────
DATA_PATH = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\data\final_analysis_dataset_new.xlsx")
OUT_DIR   = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\output\figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Колонки хорд ─────────────────────────────────────────────────────────────
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
# ШАГ 1. Загрузка, фильтрация, классификация
# ═══════════════════════════════════════════════════════════════════════════
df_raw = pd.read_excel(DATA_PATH)
print(f"Исходный датасет: {df_raw.shape[0]} × {df_raw.shape[1]}")

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

# ── Таблица частот ───────────────────────────────────────────────────────────
print("\n── Распределение Chord_Spread_Class ──")
freq = df["Chord_Spread_Class"].value_counts()
for grp in GROUP_ORDER:
    n = freq.get(grp, 0)
    print(f"  {grp:<20}: n = {n:>3}  ({100*n/len(df):.1f}%)")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 2. Kruskal-Wallis + Dunn's post-hoc (FDR — Benjamini-Hochberg)
# ═══════════════════════════════════════════════════════════════════════════

def fdr_bh(p_values):
    """Benjamini-Hochberg FDR correction для списка p-значений."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * n
    prev = 1.0
    for rank, (orig_idx, p) in enumerate(reversed(indexed), start=1):
        adj = min(prev, p * n / (n - rank + 1))
        adjusted[orig_idx] = adj
        prev = adj
    return adjusted


def dunn_fdr(df, group_col, value_col, groups):
    """Попарный тест Манна-Уитни с поправкой FDR (BH)."""
    pairs    = list(combinations(groups, 2))
    p_raws   = []
    u_stats  = []
    for g1, g2 in pairs:
        x1 = df.loc[df[group_col] == g1, value_col].dropna()
        x2 = df.loc[df[group_col] == g2, value_col].dropna()
        if len(x1) < 2 or len(x2) < 2:
            u_stats.append(np.nan)
            p_raws.append(1.0)
        else:
            u, p = stats.mannwhitneyu(x1, x2, alternative="two-sided")
            u_stats.append(u)
            p_raws.append(p)

    p_adjs = fdr_bh(p_raws)
    rows = []
    for (g1, g2), u, p_raw, p_adj in zip(pairs, u_stats, p_raws, p_adjs):
        rows.append({
            "Group 1": g1, "Group 2": g2,
            "U": u, "p (raw)": p_raw, "p (FDR-BH)": p_adj,
        })
    return pd.DataFrame(rows)


print("\n" + "═"*68)
print("  KRUSKAL-WALLIS + POST-HOC ДАННА (поправка FDR Benjamini-Hochberg)")
print("═"*68)

kw_results = {}
valid_groups = [g for g in GROUP_ORDER if g in df["Chord_Spread_Class"].values]

for target in TARGETS:
    groups_data = [
        df.loc[df["Chord_Spread_Class"] == g, target].dropna().values
        for g in valid_groups
    ]
    H, p = stats.kruskal(*groups_data)
    kw_results[target] = {"H": H, "p": p}

    sig_label = "✓ ЗНАЧИМО" if p < 0.05 else "✗ незначимо"
    print(f"\n  [{TARGET_LABELS[target].split(',')[0]}]")
    print(f"    Kruskal-Wallis  H = {H:.4f},  p = {p:.4f}  → {sig_label}")
    print(f"    Медианы по группам:")
    for g, gd in zip(valid_groups, groups_data):
        q1, q3 = np.percentile(gd, [25, 75]) if len(gd) > 1 else (np.nan, np.nan)
        print(f"      {g:<22}: median = {np.median(gd):.2f}  "
              f"[IQR {q1:.2f}–{q3:.2f}]  n={len(gd)}")

    if p < 0.05:
        print(f"\n    Post-hoc Dunn (FDR-BH):")
        ph = dunn_fdr(df, "Chord_Spread_Class", target, valid_groups)
        for _, row in ph.iterrows():
            sig_ph = "* p<0.05" if row["p (FDR-BH)"] < 0.05 else "n.s."
            print(f"      {row['Group 1']!s:<22} vs {row['Group 2']!s:<22}: "
                  f"p_raw={row['p (raw)']:.4f}  "
                  f"p_FDR={row['p (FDR-BH)']:.4f}  {sig_ph}")
    else:
        print("    → Post-hoc не требуется (глобальный тест незначим)")

print("\n" + "═"*68)

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 3. Q1-style Visualization
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
    "dicor_ssou_cv_pct":    "spread_vs_ssou.png",
    "dicor_sm_kdtr_cv_pct": "spread_vs_kdtr.png",
}

X_LABEL = "Chord Spatial Spread Class"

df_plot = df[df["Chord_Spread_Class"].isin(valid_groups)].copy()

for target in TARGETS:
    fig, ax = plt.subplots(figsize=(5.5, 4.8))

    # 1. Boxplot — белый ящик, чёрные линии
    sns.boxplot(
        data=df_plot,
        x="Chord_Spread_Class", y=target,
        order=valid_groups,
        color="white",
        linecolor="black",
        linewidth=0.9,
        fliersize=0,
        width=0.52,
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
        alpha=0.70,
        jitter=True,
        size=4.2,
        ax=ax,
    )

    # 3. Подписи осей (без title)
    ax.set_xlabel(X_LABEL, fontsize=11, labelpad=9)
    ax.set_ylabel(TARGET_LABELS[target], fontsize=11, labelpad=9)
    ax.set_title("")

    # 4. Аннотация KW в правом верхнем углу
    H_val = kw_results[target]["H"]
    p_val = kw_results[target]["p"]
    p_str = f"p = {p_val:.3f}" if p_val >= 0.001 else "p < 0.001"
    kw_ann = f"Kruskal–Wallis H = {H_val:.2f}\n{p_str}"
    ax.text(0.97, 0.97, kw_ann,
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=8.5, color="black", style="italic",
            multialignment="right",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="lightgrey", linewidth=0.7))

    # 5. N в подписях оси X
    xtick_labels = []
    for grp in valid_groups:
        n = (df_plot["Chord_Spread_Class"] == grp).sum()
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

print("\n✓ Spatial Spread analysis завершён.")
