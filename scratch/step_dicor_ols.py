"""
DICOR Analysis: OLS-регрессия двух таргетов DICOR
на количество хорд + геометрические ковариаты.
"""

import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.preprocessing import StandardScaler

# ── Пути ────────────────────────────────────────────────────────────────────
DATA_PATH = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_new.xlsx"
OUT_DIR   = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\output\figures"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Переменные ───────────────────────────────────────────────────────────────
TARGETS = [
    "dicor_ssou_cv_pct",
    "dicor_sm_kdtr_cv_pct",
]
TARGET_LABELS = {
    "dicor_ssou_cv_pct":     "DICOR SSOU CV%",
    "dicor_sm_kdtr_cv_pct":  "DICOR SM KDTR CV%",
}

PREDICTOR = "lv_false_tendon_total_count"   # НЕ стандартизируем

COV_COLS = [
    "echo_lv_ejection_fraction_teichholz_pct",
    "echo_lv_end_diastolic_volume_teichholz_ml",
    "echo_lv_sphericity_index_end_diastolic_ratio",
]
COV_LABELS = {
    "echo_lv_ejection_fraction_teichholz_pct":      "EF (Teichholz) [Z]",
    "echo_lv_end_diastolic_volume_teichholz_ml":    "EDV (Teichholz) [Z]",
    "echo_lv_sphericity_index_end_diastolic_ratio": "Sphericity Index [Z]",
}

ALL_REQUIRED = TARGETS + [PREDICTOR] + COV_COLS

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 1. Загрузка и фильтрация
# ═══════════════════════════════════════════════════════════════════════════
df_raw = pd.read_excel(DATA_PATH)
print(f"Исходный датасет: {df_raw.shape[0]} строк × {df_raw.shape[1]} колонок")

# Проверяем наличие колонок
missing_cols = [c for c in ALL_REQUIRED if c not in df_raw.columns]
if missing_cols:
    raise ValueError(f"Колонки отсутствуют в датасете: {missing_cols}")

# Листвайз-удаление: только строки без пропусков во ВСЕХ нужных переменных
df = df_raw[ALL_REQUIRED].dropna().copy()
print(f"После листвайз-удаления (все нужные переменные): n = {len(df)}")
print(f"  Исключено строк: {df_raw.shape[0] - len(df)}")

# ── Z-стандартизация (targets + covariates, НЕ предиктор) ────────────────────
scaler = StandardScaler()
cols_to_scale = TARGETS + COV_COLS

scaled_vals = scaler.fit_transform(df[cols_to_scale])
scaled_df   = pd.DataFrame(scaled_vals, columns=[c + "_z" for c in cols_to_scale],
                            index=df.index)
df = pd.concat([df, scaled_df], axis=1)

Z_TARGETS = [t + "_z" for t in TARGETS]
Z_COVS    = [c + "_z" for c in COV_COLS]

print("\n── Проверка Z-стандартизации (mean ≈ 0, std ≈ 1) ──")
for col in cols_to_scale:
    z = col + "_z"
    print(f"  {col[-30:]:<32}  mean={df[z].mean():.4f}  std={df[z].std():.4f}")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 2. Моделирование OLS
# ═══════════════════════════════════════════════════════════════════════════

def fit_ols(y_col_z, y_col_orig, df, predictor, z_cov_cols):
    """Подгоняет OLS с HC3 SE; возвращает результаты в DataFrame."""
    y = df[y_col_z].values
    x_cols = [predictor] + z_cov_cols
    X = sm.add_constant(df[x_cols].values)
    res = sm.OLS(y, X).fit(cov_type="HC3")

    conf_int = np.array(res.conf_int())   # shape (k, 2)
    rows = []
    names = ["const"] + x_cols
    for i, name in enumerate(names):
        rows.append({
            "target":   y_col_orig,   # всегда оригинальное имя
            "_varname": name,
            "beta":     res.params[i],
            "ci_lo":    conf_int[i, 0],
            "ci_hi":    conf_int[i, 1],
            "pval":     res.pvalues[i],
            "r2":       res.rsquared,
            "r2_adj":   res.rsquared_adj,
            "f_stat":   res.fvalue,
            "f_pval":   res.f_pvalue,
            "n":        int(res.nobs),
        })
    return pd.DataFrame(rows), res

results_list = []
fit_dict     = {}

for target_z, target_orig in zip(Z_TARGETS, TARGETS):
    df_res, res_obj = fit_ols(target_z, target_orig, df, PREDICTOR, Z_COVS)
    results_list.append(df_res)
    fit_dict[target_orig] = (df_res, res_obj)
    print(f"\n  {TARGET_LABELS[target_orig]}  |  R²={res_obj.rsquared:.3f}  "
          f"adj.R²={res_obj.rsquared_adj:.3f}  "
          f"F({res_obj.df_model:.0f},{res_obj.df_resid:.0f})={res_obj.fvalue:.3f}  "
          f"p={res_obj.f_pvalue:.4f}")

results_all = pd.concat(results_list, ignore_index=True)

# ── Читабельные имена ────────────────────────────────────────────────────────
name_map = {"const": "Intercept", PREDICTOR: "Chord count"}
name_map.update({c + "_z": COV_LABELS[c] for c in COV_COLS})

results_all["Predictor"] = results_all["_varname"].map(name_map)

def stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "†"
    return ""

results_all["Beta (95% CI)"] = results_all.apply(
    lambda r: f"{r.beta:+.3f} [{r.ci_lo:+.3f}; {r.ci_hi:+.3f}]", axis=1)
results_all["p-value"] = results_all.apply(
    lambda r: f"{r.pval:.4f}{stars(r.pval)}", axis=1)
results_all["Target"] = results_all["target"].map(TARGET_LABELS)

# ── Вывод таблицы ────────────────────────────────────────────────────────────
print("\n" + "═"*78)
print("  СВОДНАЯ ТАБЛИЦА OLS  |  Z-стандартизованные Y и ковариаты  |  HC3 SE")
print("═"*78)
for target_orig, target_label in TARGET_LABELS.items():
    subset = results_all[results_all["target"] == target_orig]
    first  = subset.iloc[0]
    print(f"\n  ▶ {target_label}  "
          f"[n={first.n}  R²={first.r2:.3f}  adj.R²={first.r2_adj:.3f}  "
          f"F={first.f_stat:.3f}  p={first.f_pval:.4f}]")
    print(f"  {'Predictor':<28} {'Beta (95% CI)':>34}  {'p-value':>12}")
    print("  " + "─"*76)
    for _, row in subset.iterrows():
        print(f"  {row.Predictor:<28} {row['Beta (95% CI)']:>34}  {row['p-value']:>12}")

print("\n" + "═"*78)
print("  * p<0.05  ** p<0.01  *** p<0.001  † p<0.10")
print("  Все Y и ковариаты Z-стандартизованы; chord count — в исходных единицах")
print("═"*78)

# ── Аналитический вывод ──────────────────────────────────────────────────────
print("\n── Аналитический вывод ──")
for target_orig, target_label in TARGET_LABELS.items():
    row = results_all[
        (results_all["target"] == target_orig) &
        (results_all["_varname"] == PREDICTOR)
    ].iloc[0]
    direction = "увеличивает" if row.beta > 0 else "снижает"
    significance = "значим (p < 0.05)" if row.pval < 0.05 else f"незначим (p = {row.pval:.4f})"
    print(f"\n  [{target_label}]")
    print(f"    Chord count: β = {row.beta:+.4f}, 95% CI [{row.ci_lo:+.4f}; {row.ci_hi:+.4f}], p = {row.pval:.4f}")
    print(f"    → Эффект {significance}, направление: {direction} CV%")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 3. Forest Plots (1 строка × 2 колонки)
# ═══════════════════════════════════════════════════════════════════════════

BG_DARK   = "#0D1117"
BG_PANEL  = "#161B22"
BG_STRIP1 = "#1C2128"
BG_STRIP2 = "#161B22"
COL_ZERO  = "#E74C3C"
COL_SIG   = "#2ECC71"
COL_NULL  = "#607080"
COL_GRID  = "#21262D"
COL_TEXT  = "#E6EDF3"
COL_MUTED = "#8B949E"
FONT      = "DejaVu Sans"

fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=False)
fig.patch.set_facecolor(BG_DARK)

for ax_idx, (target_orig, target_label) in enumerate(TARGET_LABELS.items()):
    ax = axes[ax_idx]
    ax.set_facecolor(BG_PANEL)

    df_res, res_obj = fit_dict[target_orig]
    plot_df = df_res[df_res["_varname"] != "const"].reset_index(drop=True)
    plot_df["label"] = plot_df["_varname"].map(name_map)

    n_rows = len(plot_df)
    y_pos  = np.arange(n_rows)[::-1]

    # Чередующиеся полосы фона
    for i, yp in enumerate(y_pos):
        ax.axhspan(yp - 0.48, yp + 0.48,
                   facecolor=BG_STRIP1 if i % 2 == 0 else BG_STRIP2,
                   zorder=1)

    # Линия нулевого эффекта
    ax.axvline(0, color=COL_ZERO, linestyle="--", linewidth=1.6,
               alpha=0.9, zorder=3, label="No effect")

    # Точки и доверительные интервалы
    for i, (_, row) in enumerate(plot_df.iterrows()):
        yp = y_pos[i]
        ci_crosses_zero = row.ci_lo <= 0 <= row.ci_hi
        color = COL_NULL if ci_crosses_zero else COL_SIG

        # "Ус" (errorbar)
        ax.errorbar(
            x=row.beta, y=yp,
            xerr=[[row.beta - row.ci_lo], [row.ci_hi - row.beta]],
            fmt="none",
            ecolor=color, elinewidth=2.2,
            capsize=6, capthick=2.2,
            zorder=4,
        )
        # Маркер
        ax.scatter(row.beta, yp, s=90, color=color,
                   zorder=5, edgecolors="white", linewidths=0.6)

        # p-value справа от CI
        p_str = f"p = {row.pval:.3f}"
        if row.pval < 0.001: p_str = "p < 0.001 ***"
        elif row.pval < 0.01:  p_str += " **"
        elif row.pval < 0.05:  p_str += " *"
        elif row.pval < 0.10:  p_str += " †"

        x_right = plot_df["ci_hi"].max() + (plot_df["ci_hi"].max() - plot_df["ci_lo"].min()) * 0.05
        ax.text(x_right, yp, p_str,
                va="center", ha="left", fontsize=8.5,
                color=COL_MUTED, fontfamily=FONT, zorder=6)

    # Оси
    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["label"].tolist(),
                       fontsize=11, color=COL_TEXT, fontfamily=FONT)
    ax.set_xlabel("Standardized β coefficient", fontsize=10.5,
                  color=COL_TEXT, labelpad=8, fontfamily=FONT)

    # Заголовок
    r2_line  = f"n = {res_obj.nobs:.0f}  |  R² = {res_obj.rsquared:.3f}  |  adj. R² = {res_obj.rsquared_adj:.3f}"
    f_line   = f"F({res_obj.df_model:.0f},{res_obj.df_resid:.0f}) = {res_obj.fvalue:.2f}  |  p = {res_obj.f_pvalue:.4f}"
    ax.set_title(
        f"{target_label}\n{r2_line}\n{f_line}",
        fontsize=10.5, color=COL_TEXT, pad=10,
        fontfamily=FONT, fontweight="bold", linespacing=1.6,
    )

    # Стиль осей
    ax.tick_params(axis="x", colors=COL_MUTED, labelsize=9)
    ax.tick_params(axis="y", left=False)
    for sp in ax.spines.values():
        sp.set_edgecolor("#30363D")
    ax.xaxis.grid(True, color=COL_GRID, linestyle=":", linewidth=0.9, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)

    # X-диапазон с запасом для аннотаций
    x_all   = pd.concat([plot_df["ci_lo"], plot_df["ci_hi"]])
    x_range = x_all.max() - x_all.min()
    ax.set_xlim(x_all.min() - x_range * 0.08,
                x_all.max() + x_range * 0.55)
    ax.set_ylim(-0.7, n_rows - 0.3)

# Общая легенда
sig_p  = mpatches.Patch(color=COL_SIG,  label="CI не пересекает 0")
null_p = mpatches.Patch(color=COL_NULL, label="CI пересекает 0")
zero_l = plt.Line2D([0], [0], color=COL_ZERO, linestyle="--",
                    linewidth=1.6, label="Нет эффекта (β = 0)")
fig.legend(handles=[sig_p, null_p, zero_l],
           loc="lower center", ncol=3,
           fontsize=9.5, facecolor=BG_STRIP1,
           edgecolor="#30363D", labelcolor=COL_TEXT,
           bbox_to_anchor=(0.5, -0.04))

# Общий заголовок
fig.suptitle(
    "OLS Regression: DICOR Variability ~ Chord Count + Geometry Covariates\n"
    "(HC3 robust SE  |  Z-standardized outcomes and covariates)",
    fontsize=13, color=COL_TEXT, fontweight="bold",
    fontfamily=FONT, y=1.02,
)

plt.tight_layout(rect=[0, 0.04, 1, 1])

out_path = os.path.join(OUT_DIR, "dicor_ols_forest_plot.png")
fig.savefig(out_path, dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\nForest plot сохранён: {out_path}")
print("✓ Анализ DICOR завершён.")
