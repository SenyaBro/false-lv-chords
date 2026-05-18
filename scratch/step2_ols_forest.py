"""
Шаг 2. OLS-регрессия: количество хорд → echo_lv_strain_plus_cv_pct
         + Forest Plot результатов.
"""

import sys, os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Пути ────────────────────────────────────────────────────────────────────
DATA_PATH   = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_new.xlsx"
OUT_DIR     = r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\output\figures"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Колонки ──────────────────────────────────────────────────────────────────
OUTCOME   = "echo_lv_strain_plus_cv_pct"
PREDICTOR = "lv_false_tendon_total_count"
COV_COLS  = [
    "echo_lv_ejection_fraction_simpson_pct",
    "echo_lv_end_diastolic_volume_simpson_ml",
    "echo_lv_sphericity_index_end_diastolic_ratio",
]
ALL_COLS  = [OUTCOME, PREDICTOR] + COV_COLS

LABELS = {
    PREDICTOR:  "Chord count",
    "echo_lv_ejection_fraction_simpson_pct":        "EF (Simpson) [Z]",
    "echo_lv_end_diastolic_volume_simpson_ml":      "EDV (Simpson) [Z]",
    "echo_lv_sphericity_index_end_diastolic_ratio": "Sphericity Index (ED) [Z]",
}

# ── 1. Загрузка и фильтрация ─────────────────────────────────────────────────
df_raw = pd.read_excel(DATA_PATH)
df = df_raw.dropna(subset=[OUTCOME]).copy()
print(f"Когорта (есть outcome): n = {len(df)}")

# ── 2. Z-стандартизация ковариат ─────────────────────────────────────────────
Z_COLS = []
for col in COV_COLS:
    z = col + "_z"
    df[z] = (df[col] - df[col].mean()) / df[col].std(ddof=1)
    Z_COLS.append(z)

# ── 3. Подготовка матрицы для OLS ────────────────────────────────────────────
model_cols = [PREDICTOR] + Z_COLS
df_model = df[[OUTCOME] + model_cols].dropna()
print(f"Полные случаи для модели: n = {len(df_model)}")

y = df_model[OUTCOME].values
X_raw = df_model[model_cols].values
X = sm.add_constant(X_raw)   # добавляем интерсепт

# ── 4. Подгонка OLS ──────────────────────────────────────────────────────────
model = sm.OLS(y, X)
res   = model.fit(cov_type="HC3")   # гетероскедастически-робастные SE (n=32)

# ── 5. Сводная таблица для статьи ────────────────────────────────────────────
conf_int = pd.DataFrame(res.conf_int(), columns=["lo", "hi"])
param_names = ["Intercept"] + model_cols
z_name_map = {v + "_z": LABELS[v] for v in COV_COLS}
z_name_map[PREDICTOR] = LABELS[PREDICTOR]

rows = []
for i, name in enumerate(param_names):
    if name == "const":
        display = "Intercept"
    else:
        display = z_name_map.get(name, name)

    beta = res.params[i]
    ci_lo, ci_hi = conf_int.iloc[i]["lo"], conf_int.iloc[i]["hi"]
    pval = res.pvalues[i]

    stars = ""
    if pval < 0.001: stars = "***"
    elif pval < 0.01: stars = "**"
    elif pval < 0.05: stars = "*"
    elif pval < 0.10: stars = "†"

    rows.append({
        "Predictor":          display,
        "Beta (95% CI)":      f"{beta:+.3f} [{ci_lo:+.3f}; {ci_hi:+.3f}]",
        "p-value":            f"{pval:.4f}{stars}",
        "_beta":   beta,
        "_ci_lo":  ci_lo,
        "_ci_hi":  ci_hi,
        "_pval":   pval,
        "_name":   name,
    })

df_table = pd.DataFrame(rows)

print("\n" + "═"*70)
print("  OLS results  |  Y = echo_lv_strain_plus_cv_pct  |  HC3 robust SE")
print(f"  n = {len(df_model)}  |  R² = {res.rsquared:.3f}  |  adj. R² = {res.rsquared_adj:.3f}")
print("═"*70)
print(df_table[["Predictor","Beta (95% CI)","p-value"]].to_string(index=False))
print("─"*70)
print("  * p<0.05  ** p<0.01  *** p<0.001  † p<0.10")
print(f"  Model F({res.df_model:.0f},{res.df_resid:.0f}) = {res.fvalue:.3f}  p = {res.f_pvalue:.4f}")
print("═"*70)

# ── 6. Forest Plot ───────────────────────────────────────────────────────────
# Только предикторы (без интерсепта)
plot_rows = df_table[df_table["_name"] != "const"].reset_index(drop=True)

# Цвет: зелёный если CI не пересекает 0, иначе серый
def ci_color(row):
    if row["_ci_lo"] > 0 or row["_ci_hi"] < 0:
        return "#2ECC71"   # значимо
    return "#7F8C8D"       # пересекает ноль

colors = [ci_color(r) for _, r in plot_rows.iterrows()]

fig, ax = plt.subplots(figsize=(9, 4.5))
fig.patch.set_facecolor("#0F1117")
ax.set_facecolor("#0F1117")

y_pos = np.arange(len(plot_rows))[::-1]   # сверху вниз

for i, (_, row) in enumerate(plot_rows.iterrows()):
    yp = y_pos[i]
    c  = colors[i]
    ax.errorbar(
        x=row["_beta"],
        y=yp,
        xerr=[[row["_beta"] - row["_ci_lo"]], [row["_ci_hi"] - row["_beta"]]],
        fmt="o",
        color=c,
        ecolor=c,
        elinewidth=2.0,
        capsize=5,
        capthick=2.0,
        markersize=8,
        zorder=4,
    )
    # p-value аннотация справа
    p_txt = f"p = {row['_pval']:.3f}"
    ax.text(
        ax.get_xlim()[1] if ax.get_xlim()[1] else row["_ci_hi"] + 0.5,
        yp,
        p_txt,
        va="center", ha="left",
        fontsize=8.5, color="#BDC3C7",
        zorder=5,
    )

# Вертикальная линия нулевого эффекта
ax.axvline(0, color="#E74C3C", linestyle="--", linewidth=1.5, alpha=0.8, zorder=3)

# Оси
ax.set_yticks(y_pos)
ax.set_yticklabels(plot_rows["Predictor"].tolist(), fontsize=11, color="white")
ax.set_xlabel("Beta coefficient (effect on CV%)", fontsize=11, color="white", labelpad=8)
ax.set_title(
    "OLS Forest Plot\nY = echo_lv_strain_plus_cv_pct  |  HC3 robust SE  |  n = " + str(len(df_model)),
    fontsize=12, color="white", pad=12, fontweight="bold"
)

# Оформление
ax.tick_params(axis="x", colors="white", labelsize=9)
ax.tick_params(axis="y", colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#3D4452")

ax.xaxis.grid(True, color="#2C3E50", linestyle=":", linewidth=0.8, alpha=0.7)
ax.set_axisbelow(True)

# Полоски зебры
for i, yp in enumerate(y_pos):
    ax.axhspan(yp - 0.45, yp + 0.45,
               facecolor="#1A1D27" if i % 2 == 0 else "#0F1117",
               zorder=1)

# Легенда
sig_patch  = mpatches.Patch(color="#2ECC71", label="CI не пересекает 0")
null_patch = mpatches.Patch(color="#7F8C8D", label="CI пересекает 0")
ax.legend(handles=[sig_patch, null_patch],
          loc="lower right", fontsize=9,
          facecolor="#1A1D27", edgecolor="#3D4452",
          labelcolor="white")

# R² аннотация
r2_text = f"R² = {res.rsquared:.3f}  |  adj. R² = {res.rsquared_adj:.3f}"
fig.text(0.98, 0.02, r2_text, ha="right", va="bottom",
         fontsize=9, color="#95A5A6", style="italic")

# ── Авто-масштаб оси X с отступом для аннотаций ─────────────────────────────
x_min = plot_rows["_ci_lo"].min()
x_max = plot_rows["_ci_hi"].max()
x_pad = (x_max - x_min) * 0.15
ax.set_xlim(x_min - x_pad, x_max + x_pad * 3.5)

plt.tight_layout()

out_path = os.path.join(OUT_DIR, "step2_forest_plot.png")
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"\nForest plot сохранён: {out_path}")

# ── 7. Краткий вывод ─────────────────────────────────────────────────────────
print("\n── Аналитический вывод ──")
chord_row = plot_rows[plot_rows["_name"] == PREDICTOR].iloc[0]
print(f"  Chord count:  β = {chord_row['_beta']:+.3f}, "
      f"95% CI [{chord_row['_ci_lo']:+.3f}; {chord_row['_ci_hi']:+.3f}], "
      f"p = {chord_row['_pval']:.4f}")

strongest = plot_rows.loc[plot_rows["_beta"].abs().idxmax()]
print(f"  Наибольший эффект: «{strongest['Predictor']}» "
      f"(β = {strongest['_beta']:+.3f}, p = {strongest['_pval']:.4f})")
