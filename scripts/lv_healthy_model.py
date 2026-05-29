import os
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ ЗДОРОВОЙ МОДЕЛИ
# ==============================================================================
N_THETA = 42          # Разрешение по окружности
N_Z = 20              # Разрешение по высоте
N_FRAMES = 30         

# Физиологические параметры здорового ЛЖ
RADIAL_CONTRACTION = 0.33      # Симметричное радиальное сжатие эндокарда (33%)
EPICARD_CONTRACTION = 0.12      # Сжатие эпикарда (12%) -> физиологическое утолщение
TWIST_STRENGTH = 0.42          # Нормальный угол скручивания
LONGITUDINAL_SHORTENING = 0.16 # Нормальное продольное укорочение

H_BASE = 5.5
R_ENDO_BASE = 2.0              
THICKNESS_BASE = 0.6           # Базовая толщина миокарда (6 мм)

SECTOR_NAMES = ["Anterior", "Anteroseptal", "Inferoseptal", "Inferior", "Inferolateral", "Anterolateral"]

print("Сборка полностью ЗДОРОВОЙ 18-сегментной модели ЛЖ...")

# ==============================================================================
# 2. РЕФЕРЕНСНАЯ СЕТКА И АНАТОМИЧЕСКИЕ ИМЕНА
# ==============================================================================
z_ref = np.linspace(0.001, H_BASE, N_Z)
theta_ref = np.linspace(0, 2 * np.pi, N_THETA)
Z_REF, THETA_REF = np.meshgrid(z_ref, theta_ref, indexing='ij')

SEG_NAMES = np.zeros_like(Z_REF, dtype=object)

for i in range(N_Z):
    for j in range(N_THETA):
        z_ratio = Z_REF[i, j] / H_BASE
        if z_ratio > 0.66:   lvl, l_name = 0, "Basal"
        elif z_ratio > 0.33: lvl, l_name = 1, "Mid"
        else:                lvl, l_name = 2, "Apical"
        
        angle = (THETA_REF[i, j] + np.pi/6) % (2 * np.pi)
        sec = int(angle // (np.pi / 3)) % 6
        seg_id = lvl * 6 + sec + 1
        SEG_NAMES[i, j] = f"Seg {seg_id}: {l_name} {SECTOR_NAMES[sec]}"

# Индексы крепления хорд (внутри полости эндокарда)
chords_config = [
    {"name": "Поперечная ложная хорда (Mid-LV)", "color": "#00E5FF", "p1": (int(N_Z*0.5), 0), "p2": (int(N_Z*0.5), int(N_THETA*0.5))},
    {"name": "Косая ложная хорда (Apex-Base)", "color": "#FF007F", "p1": (int(N_Z*0.8), int(N_THETA*0.15)), "p2": (int(N_Z*0.2), int(N_THETA*0.65))}
]

# ==============================================================================
# 3. КИНЕМАТИЧЕСКИЙ РАСЧЕТ ЗДОРОВОГО ЦИКЛА
# ==============================================================================
frames_data = []
t_steps = np.linspace(0, np.pi, N_FRAMES)
contraction_curve = np.sin(t_steps)

for f in range(N_FRAMES):
    act = contraction_curve[f]
    
    # Деформации осей
    z_f = Z_REF * (1.0 - LONGITUDINAL_SHORTENING * act * (Z_REF / H_BASE))
    twist_angle = TWIST_STRENGTH * act * (Z_REF / H_BASE - 0.35)
    theta_f = THETA_REF + twist_angle
    
    # Радиусы стенок (ЗДОРОВЫЕ - БЕЗ КАРТЫ ПАТОЛОГИЙ)
    r_endo_ref = R_ENDO_BASE * np.sqrt(1 - ((H_BASE - Z_REF) / H_BASE) ** 2)
    r_epi_ref = (R_ENDO_BASE + THICKNESS_BASE) * np.sqrt(1 - ((H_BASE - Z_REF) / (H_BASE + THICKNESS_BASE)) ** 2)
    
    r_endo_f = r_endo_ref * (1.0 - RADIAL_CONTRACTION * act)
    r_epi_f = r_epi_ref * (1.0 - EPICARD_CONTRACTION * act)
    
    # Вычисление физиологических параметров
    current_thickness = r_epi_f - r_endo_f
    strain_f = -((r_endo_ref - r_endo_f) / r_endo_ref) * 100.0
    
    # Координаты слоев
    X_end, Y_end = r_endo_f * np.cos(theta_f), r_endo_f * np.sin(theta_f)
    X_epi, Y_epi = r_epi_f * np.cos(theta_f), r_epi_f * np.sin(theta_f)
    
    # Пересчет динамического положения хорд
    chords_coords = []
    for chord in chords_config:
        z1, t1 = chord["p1"]
        z2, t2 = chord["p2"]
        chords_coords.append((
            (X_end[z1, t1], Y_end[z1, t1], z_f[z1, t1]),
            (X_end[z2, t2], Y_end[z2, t2], z_f[z2, t2])
        ))
        
    frames_data.append({
        "X_end": X_end, "Y_end": Y_end, "Z": z_f,
        "X_epi": X_epi, "Y_epi": Y_epi,
        "strain": strain_f, "thickness": current_thickness,
        "chords": chords_coords
    })

# ==============================================================================
# 4. СБОРКА ИНТЕРАКТИВНОЙ 3D СЦЕНЫ
# ==============================================================================
init_f = frames_data[0]

hover_text = np.zeros_like(Z_REF, dtype=object)
for i in range(N_Z):
    for j in range(N_THETA):
        hover_text[i, j] = f"{SEG_NAMES[i, j]}<br>Strain: {init_f['strain'][i, j]:.1f}%<br>Толщина стенки: {init_f['thickness'][i, j]:.2f} см"

# Внутренний эндокард (Здоровый однородный Strain)
endo_surface = go.Surface(
    x=init_f["X_end"], y=init_f["Y_end"], z=init_f["Z"],
    surfacecolor=init_f["strain"],
    colorscale="Jet", cmin=-40.0, cmax=0.0,
    colorbar=dict(title="Физиологический Strain (%)", thickness=20, len=0.6),
    opacity=0.95, text=hover_text, hoverinfo="text", name="Эндокард"
)

# Внешний полупрозрачный эпикард
epi_surface = go.Surface(
    x=init_f["X_epi"], y=init_f["Y_epi"], z=init_f["Z"],
    surfacecolor=np.zeros_like(Z_REF),
    colorscale=[[0, "rgba(90, 100, 110, 0.2)"], [1, "rgba(90, 100, 110, 0.2)"]], 
    showscale=False, opacity=0.25, hoverinfo="skip", name="Эпикард"
)

# Белые линии-маркеры Twist (на эпикарде)
twist_lines = []
for j in range(0, N_THETA, 6):
    twist_lines.append(go.Scatter3d(
        x=init_f["X_epi"][:, j], y=init_f["Y_epi"][:, j], z=init_f["Z"][:, j],
        mode="lines", line=dict(color="rgba(255, 255, 255, 0.75)", width=3),
        showlegend=False, hoverinfo="skip"
    ))

# Добавление хорд во внутреннюю полость
chords_plots = []
for idx, chord in enumerate(chords_config):
    p1, p2 = init_f["chords"][idx]
    chords_plots.append(go.Scatter3d(
        x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]],
        mode="lines+markers", line=dict(color=chord["color"], width=6),
        marker=dict(size=4, color="white"), name=chord["name"]
    ))

plot_data = [endo_surface, epi_surface] + twist_lines + chords_plots

# Сборка кадров
plotly_frames = []
for f in range(N_FRAMES):
    f_info = frames_data[f]
    
    f_hover = np.zeros_like(Z_REF, dtype=object)
    for i in range(N_Z):
        for j in range(N_THETA):
            f_hover[i, j] = f"{SEG_NAMES[i, j]}<br>Strain: {f_info['strain'][i, j]:.1f}%<br>Толщина стенки: {f_info['thickness'][i, j]:.2f} см"
            
    frame_traces = [
        go.Surface(x=f_info["X_end"], y=f_info["Y_end"], z=f_info["Z"], surfacecolor=f_info["strain"], text=f_hover),
        go.Surface(x=f_info["X_epi"], y=f_info["Y_epi"], z=f_info["Z"])
    ]
    
    # Линии скручивания
    for j in range(0, N_THETA, 6):
        frame_traces.append(go.Scatter3d(x=f_info["X_epi"][:, j], y=f_info["Y_epi"][:, j], z=f_info["Z"][:, j]))
        
    # Движение ложных хорд
    for idx in range(len(chords_config)):
        p1, p2 = f_info["chords"][idx]
        frame_traces.append(go.Scatter3d(x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]]))
        
    plotly_frames.append(go.Frame(data=frame_traces, name=f"frame_{f}"))

# Интерфейс
layout = go.Layout(
    title=dict(text="Здоровая 18-сегментная биомеханическая модель ЛЖ с ложными хордами", x=0.5, font=dict(color="white")),
    template="plotly_dark",
    scene=dict(
        xaxis=dict(title="X (cm)", range=[-3.3, 3.3], gridcolor="#222"),
        yaxis=dict(title="Y (cm)", range=[-3.3, 3.3], gridcolor="#222"),
        zaxis=dict(title="Z (cm)", range=[-0.2, 5.8], gridcolor="#222"),
        camera=dict(eye=dict(x=1.4, y=1.4, z=0.6)),
        aspectratio=dict(x=1, y=1, z=1.1)
    ),
    updatemenus=[{
        "type": "buttons", "direction": "left", "pad": {"r": 10, "t": 85},
        "buttons": [
            {"label": "▶ Запустить цикл ЛЖ", "method": "animate", "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]},
            {"label": "⏸ Пауза", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ], "x": 0.1, "y": 0
    }],
    sliders=[{
        "active": 0, "len": 0.9, "x": 0.1, "y": 0,
        "steps": [{"args": [[f"frame_{f}"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}], "label": f"{int(f/N_FRAMES*100)}%", "method": "animate"} for f in range(N_FRAMES)]
    }]
)

fig = go.Figure(data=plot_data, layout=layout, frames=plotly_frames)

output_path = os.path.join(os.getcwd(), "lv_healthy_model.html")
fig.write_html(output_path, auto_play=False, include_plotlyjs="cdn")
print(f"\n[УСПЕШНО] Полностью здоровая модель сохранена:\n--> {output_path}\n")