"""
Poisson Regression: lv_false_tendon_total_count ~
    echo_lv_sphericity_index_end_diastolic_ratio (Z)
  + dicor_sm_kdtr_cv_pct (Z)
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns

# ── Пути ────────────────────────────────────────────────────────────────────
DATA_PATH = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\data\final_analysis_dataset_new.xlsx")
OUT_DIR   = (r"C:\Users\Ars\projects\university\lab_urfu_2026"
             r"\false-lv-chords\output\figures")
os.makedirs(OUT_DIR, exist_ok=True)

TARGET = "lv_false_tendon_total_count"
PRED_SPHER = "echo_lv_sphericity_index_end_diastolic_ratio"
PRED_KDTR  = "dicor_sm_kdtr_cv_pct"

LABEL_SPHER = "Sphericity Index (ED) [Z]"
LABEL_KDTR  = "DICOR SM KDTR CV% [Z]"

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 1. Данные
# ═══════════════════════════════════════════════════════════════════════════
df_raw = pd.read_excel(DATA_PATH)
print(f"Исходный датасет: {df_raw.shape[0]} × {df_raw.shape[1]}")

df = df_raw[[TARGET, PRED_SPHER, PRED_KDTR]].dropna().copy()
print(f"После листвайз-удаления: n = {len(df)}")

# Z-стандартизация предикторов
for col in [PRED_SPHER, PRED_KDTR]:
    z = col + "_z"
    df[z] = (df[col] - df[col].mean()) / df[col].std(ddof=1)

Z_SPHER = PRED_SPHER + "_z"
Z_KDTR  = PRED_KDTR  + "_z"

print(f"\nY (chord count) — дескриптивно:")
print(df[TARGET].value_counts().sort_index().to_string())

print(f"\nПредикторы после Z-стандартизации:")
for z in [Z_SPHER, Z_KDTR]:
    print(f"  {z[-35:]:<38}  mean={df[z].mean():.4f}  std={df[z].std():.4f}")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 2. Poisson GLM
# ═══════════════════════════════════════════════════════════════════════════
y = df[TARGET].values.astype(float)
X = sm.add_constant(df[[Z_SPHER, Z_KDTR]].values)

model = sm.GLM(y, X, family=sm.families.Poisson())
res   = model.fit()

# IRR = exp(β)
irr      = np.exp(res.params)
ci_raw   = np.array(res.conf_int())       # shape (k, 2) in log-scale
ci_irr   = np.exp(ci_raw)                 # exponentiate bounds

var_names  = ["Intercept", LABEL_SPHER, LABEL_KDTR]
var_keys   = ["const", Z_SPHER, Z_KDTR]

rows = []
for i, (name, key) in enumerate(zip(var_names, var_keys)):
    rows.append({
        "Predictor":    name,
        "_key":         key,
        "IRR":          irr[i],
        "CI_lo":        ci_irr[i, 0],
        "CI_hi":        ci_irr[i, 1],
        "pval":         res.pvalues[i],
        "log_beta":     res.params[i],
    })

df_res = pd.DataFrame(rows)

def stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "†"
    return ""

df_res["IRR (95% CI)"] = df_res.apply(
    lambda r: f"{r.IRR:.3f} [{r.CI_lo:.3f}; {r.CI_hi:.3f}]", axis=1)
df_res["p-value"] = df_res.apply(
    lambda r: f"{r.pval:.4f}{stars(r.pval)}", axis=1)

print("\n" + "═"*70)
print(f"  Poisson GLM  |  Y = lv_false_tendon_total_count  |  n = {len(df)}")
print(f"  AIC = {res.aic:.2f}  |  Deviance = {res.deviance:.3f}  "
      f"|  df = {res.df_resid:.0f}")
print("═"*70)
print(df_res[["Predictor","IRR (95% CI)","p-value"]].to_string(index=False))
print("─"*70)
print("  IRR: во сколько раз меняется ожидаемое число хорд при Δ=1 SD")
print("  * p<0.05  ** p<0.01  *** p<0.001  † p<0.10")
print("═"*70)

# ── Текстовый вывод по IRR ───────────────────────────────────────────────────
print("\n── Интерпретация IRR ──")
for _, row in df_res[df_res["_key"] != "const"].iterrows():
    direction = "больше" if row["IRR"] > 1 else "меньше"
    pct = abs(row["IRR"] - 1) * 100
    sig = "значимо" if row["pval"] < 0.05 else "незначимо"
    print(f"  {row.Predictor}")
    print(f"    IRR = {row['IRR']:.3f}  → ожидаемое число хорд "
          f"в {row['IRR']:.3f}× ({direction} на {pct:.1f}%) "
          f"при +1 SD,  p = {row['pval']:.4f} ({sig})")

# ═══════════════════════════════════════════════════════════════════════════
# ШАГ 3. Визуализация (1 × 3)
# ═══════════════════════════════════════════════════════════════════════════
BG      = "#0D1117"
PANEL   = "#161B22"
S1      = "#1C2128"
S2      = "#161B22"
CTEXT   = "#E6EDF3"
CMUTED  = "#8B949E"
CGRID   = "#21262D"
CRED    = "#E74C3C"
CGREEN  = "#2ECC71"
CBLUE   = "#3B9EFF"
CORANGE = "#F0883E"
CFONT   = "DejaVu Sans"

fig = plt.figure(figsize=(17, 5.8), facecolor=BG)
gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)

# ─────────────────────────────────────────────────────────────────────────
# ПАНЕЛЬ 1: Forest Plot (IRR)
# ─────────────────────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor(PANEL)

plot_df = df_res[df_res["_key"] != "const"].reset_index(drop=True)
y_pos   = np.arange(len(plot_df))[::-1]

for i, yp in enumerate(y_pos):
    ax1.axhspan(yp - 0.48, yp + 0.48,
                facecolor=S1 if i % 2 == 0 else S2, zorder=1)

# Линия IRR=1 (нет эффекта)
ax1.axvline(1.0, color=CRED, linestyle="--", linewidth=1.6,
            alpha=0.9, zorder=3, label="IRR = 1 (no effect)")

for i, (_, row) in enumerate(plot_df.iterrows()):
    yp = y_pos[i]
    ci_cross = row.CI_lo <= 1.0 <= row.CI_hi
    color = CMUTED if ci_cross else CGREEN

    ax1.errorbar(
        x=row.IRR, y=yp,
        xerr=[[row.IRR - row.CI_lo], [row.CI_hi - row.IRR]],
        fmt="none", ecolor=color, elinewidth=2.2,
        capsize=6, capthick=2.2, zorder=4,
    )
    ax1.scatter(row.IRR, yp, s=95, color=color,
                edgecolors="white", linewidths=0.7, zorder=5)

    p_str = f"p = {row.pval:.3f}"
    if   row.pval < 0.001: p_str = "p < 0.001***"
    elif row.pval < 0.01:  p_str += "**"
    elif row.pval < 0.05:  p_str += "*"
    elif row.pval < 0.10:  p_str += " †"

    x_ann = plot_df["CI_hi"].max() + 0.02
    ax1.text(x_ann, yp, p_str, va="center", ha="left",
             fontsize=8.5, color=CMUTED, zorder=6)

ax1.set_yticks(y_pos)
ax1.set_yticklabels(plot_df["Predictor"].tolist(),
                    fontsize=10.5, color=CTEXT)
ax1.set_xlabel("Incidence Rate Ratio (IRR)", fontsize=10,
               color=CTEXT, labelpad=7)
ax1.set_title("Forest Plot\n(Poisson IRR, 95% CI)",
              fontsize=11, color=CTEXT, fontweight="bold", pad=9)
ax1.tick_params(axis="x", colors=CMUTED, labelsize=8.5)
ax1.tick_params(axis="y", left=False)
for sp in ax1.spines.values():
    sp.set_edgecolor("#30363D")
ax1.xaxis.grid(True, color=CGRID, linestyle=":", linewidth=0.9, zorder=0)
ax1.set_axisbelow(True)

x_range = plot_df["CI_hi"].max() - plot_df["CI_lo"].min()
ax1.set_xlim(plot_df["CI_lo"].min() - x_range * 0.05,
             plot_df["CI_hi"].max() + x_range * 0.55)
ax1.set_ylim(-0.65, len(plot_df) - 0.35)

# ─────────────────────────────────────────────────────────────────────────
# ПАНЕЛЬ 2: Marginal Effect — Sphericity Index
# ─────────────────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor(PANEL)

z_grid = np.linspace(-3, 3, 200)
# KDTR зафиксирован на 0 (среднем)
X_pred = sm.add_constant(np.column_stack([z_grid, np.zeros_like(z_grid)]))
pred_obj  = res.get_prediction(X_pred)
pred_mean = pred_obj.predicted_mean
pred_ci   = pred_obj.conf_int(alpha=0.05)

ax2.fill_between(z_grid, pred_ci[:, 0], pred_ci[:, 1],
                 color=CBLUE, alpha=0.18, zorder=2, label="95% CI")
ax2.plot(z_grid, pred_mean, color=CBLUE, linewidth=2.4,
         zorder=3, label="E[chords | KDTR=mean]")

# Рассеянные точки наблюдений
ax2.scatter(df[Z_SPHER], df[TARGET],
            color=CGREEN, alpha=0.45, s=28,
            edgecolors="none", zorder=4, label="Observed")

ax2.set_xlabel(LABEL_SPHER, fontsize=10, color=CTEXT, labelpad=7)
ax2.set_ylabel("Expected chord count (λ)", fontsize=10,
               color=CTEXT, labelpad=7)
ax2.set_title("Marginal Effect\nSphericity Index → Chord Count",
              fontsize=11, color=CTEXT, fontweight="bold", pad=9)
ax2.set_xlim(-3.1, 3.1)

ax2.tick_params(axis="both", colors=CMUTED, labelsize=8.5)
for sp in ax2.spines.values():
    sp.set_edgecolor("#30363D")
ax2.xaxis.grid(True, color=CGRID, linestyle=":", linewidth=0.9, zorder=0)
ax2.yaxis.grid(True, color=CGRID, linestyle=":", linewidth=0.9, zorder=0)
ax2.set_axisbelow(True)

leg2 = ax2.legend(fontsize=8.5, facecolor=S1, edgecolor="#30363D",
                  labelcolor=CTEXT, loc="upper left")

# Аннотация: IRR для Sphericity
irr_val = df_res[df_res["_key"] == Z_SPHER]["IRR"].values[0]
ax2.text(0.97, 0.05,
         f"IRR = {irr_val:.3f} per +1 SD",
         transform=ax2.transAxes,
         ha="right", va="bottom", fontsize=8.5,
         color=CMUTED, style="italic")

# ─────────────────────────────────────────────────────────────────────────
# ПАНЕЛЬ 3: Actual vs Predicted (Boxplot + Stripplot)
# ─────────────────────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2])
ax3.set_facecolor(PANEL)

df["y_pred"] = res.predict(X)
df["y_actual"] = df[TARGET].astype(int)

chord_cats = sorted(df["y_actual"].unique())
palette    = {c: CBLUE for c in chord_cats}

# Boxplot — используем цвет напрямую, без palette-dict
bp = sns.boxplot(
    data=df, x="y_actual", y="y_pred",
    color=CBLUE,
    linewidth=1.4, fliersize=0,
    boxprops=dict(facecolor="#1E3A5F", edgecolor=CBLUE, linewidth=1.2),
    whiskerprops=dict(color=CBLUE, linewidth=1.2),
    capprops=dict(color=CBLUE, linewidth=1.5),
    medianprops=dict(color=CORANGE, linewidth=2.0),
    ax=ax3,
)

# Stripplot поверх
sns.stripplot(
    data=df, x="y_actual", y="y_pred",
    color=CGREEN, alpha=0.55, size=4.5,
    jitter=True, dodge=False, ax=ax3, zorder=4,
)

# Диагональ совершенного предсказания (по позиционным тикам, не по значениям)
# Рисуем горизонтальные ориентиры по фактическим уровням
for pos, val in enumerate(chord_cats):
    ax3.axhline(val, color=CRED, linestyle=":", linewidth=0.9,
                alpha=0.5, zorder=2)

ax3.set_xlabel("Actual chord count", fontsize=10, color=CTEXT, labelpad=7)
ax3.set_ylabel("Predicted chord count (λ)", fontsize=10,
               color=CTEXT, labelpad=7)
ax3.set_title("Model Adequacy\nActual vs Predicted",
              fontsize=11, color=CTEXT, fontweight="bold", pad=9)

ax3.tick_params(axis="both", colors=CMUTED, labelsize=8.5)
ax3.set_facecolor(PANEL)
for sp in ax3.spines.values():
    sp.set_edgecolor("#30363D")
ax3.yaxis.grid(True, color=CGRID, linestyle=":", linewidth=0.9, zorder=0)
ax3.set_axisbelow(True)

# Легенда панели 3
ref_line = plt.Line2D([0], [0], color=CRED, linestyle=":",
                      linewidth=0.9, label="True value reference")
dot_pt   = plt.Line2D([0], [0], marker="o", color="none",
                      markerfacecolor=CGREEN, markersize=6,
                      alpha=0.7, label="Patient")
ax3.legend(handles=[ref_line, dot_pt], fontsize=8.5,
           facecolor=S1, edgecolor="#30363D",
           labelcolor=CTEXT, loc="upper left")

# ─────────────────────────────────────────────────────────────────────────
# Общий заголовок
# ─────────────────────────────────────────────────────────────────────────
fig.suptitle(
    "Poisson Regression: False Chord Count ~ Sphericity Index + DICOR SM KDTR CV%\n"
    f"(n = {len(df)}  |  AIC = {res.aic:.1f}  |  Deviance = {res.deviance:.2f}  "
    f"|  df_resid = {res.df_resid:.0f})",
    fontsize=12.5, color=CTEXT, fontweight="bold", y=1.02,
)

plt.tight_layout(rect=[0, 0, 1, 1])

out_path = os.path.join(OUT_DIR, "poisson_chord_count.png")
fig.savefig(out_path, dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\nГрафик сохранён: {out_path}")
print("✓ Poisson analysis завершён.")
