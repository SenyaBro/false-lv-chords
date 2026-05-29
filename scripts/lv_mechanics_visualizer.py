import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ И ГЕОМЕТРИЧЕСКИЕ ПАРАМЕТРЫ МОДЕЛИ
# ==============================================================================
# Параметры сетки ЛЖ
N_THETA = 36          # Количество точек по окружности ЛЖ
N_Z = 18              # Количество уровней по высоте (base -> apex)
N_FRAMES = 30         # Количество кадров в сердечном цикле (диастола -> систола -> диастола)

# Параметры биомеханической деформации
CONTRACTION_STRENGTH = 0.35    # Максимальное радиальное сужение (35%)
TWIST_STRENGTH = 0.25          # Максимальный угол скручивания (в радианах, ~14 градусов)
LONGITUDINAL_SHORTENING = 0.15 # Продольное укорочение (15%)

# Базовые размеры эллипсоида ЛЖ (в условных единицах, например, см)
R_BASE = 2.5          # Радиус основания ЛЖ
H_BASE = 6.0          # Высота ЛЖ от апекса до базиса

print("Инициализация параметров биомеханической модели ЛЖ...")

# ==============================================================================
# 2. ГЕНЕРАЦИЯ ЭТАЛОННОЙ ГЕОМЕТРИИ (РЕФЕРЕНСНАЯ ДИАСТОЛА)
# ==============================================================================
# Инициализируем сетку в цилиндрических координатах
# z от 0 (apex) до H_BASE (base)
z_ref = np.linspace(0.0, H_BASE, N_Z)
theta_ref = np.linspace(0, 2 * np.pi, N_THETA, endpoint=False)
Z_REF, THETA_REF = np.meshgrid(z_ref, theta_ref, indexing='ij')

# Идеализированная эллипсоидально-коническая форма ЛЖ: r(z)
# Ближе к апексу радиус стремится к 0, на уровне базиса — максимальный скругленный переход
R_REF = R_BASE * np.sqrt(1 - ((H_BASE - Z_REF) / H_BASE) ** 2)

# Определение 17-сегментной AHA-подобной гетерогенности (Strain mapping)
# Создадим матрицу базовой сократимости для имитации региональной неоднородности
# Например, передняя стенка сокращается чуть сильнее, боковая — слабее (условная патология/особенность)
regional_heterogeneity = np.ones((N_Z, N_THETA))
for i in range(N_Z):
    for j in range(N_THETA):
        # Разделение по углам (стенки: anterior, lateral, posterior, septal)
        angle = THETA_REF[i, j]
        # Введем синусоидальную неоднородность по окружности и по высоте
        hetero_factor = 1.0 + 0.25 * np.sin(angle) * np.exp(-((Z_REF[i, j] - H_BASE/2)/(H_BASE/2))**2)
        regional_heterogeneity[i, j] = max(0.4, min(1.5, hetero_factor))

# ==============================================================================
# 3. ОПРЕДЕЛЕНИЕ АРХИТЕКТУРЫ ЛОЖНЫХ ХОРД (FALSE TENDONS)
# ==============================================================================
# Задаем хорды через индексы сетки (z_index, theta_index) для привязки к стенкам
# z_index: 0 - apex, N_Z-1 - base. theta_index: 0 до N_THETA-1
chords_config = [
    {
        "name": "Transverse Chord (Mid-LV)",
        "color": "cyan",
        "p1": (int(N_Z * 0.5), 0),                     # Стенка 1 (0 градусов)
        "p2": (int(N_Z * 0.5), int(N_THETA * 0.5))     # Противоположная стенка (180 градусов)
    },
    {
        "name": "Oblique Chord (Base-to-Mid)",
        "color": "magenta",
        "p1": (int(N_Z * 0.8), int(N_THETA * 0.25)),   # Базальный уровень (90 градусов)
        "p2": (int(N_Z * 0.3), int(N_THETA * 0.75))    # Средне-апикальный уровень (270 градусов)
    },
    {
        "name": "Distant Longitudinal Chord",
        "color": "yellow",
        "p1": (int(N_Z * 0.9), int(N_THETA * 0.0)),    # Высокий базис
        "p2": (int(N_Z * 0.1), int(N_THETA * 0.1))     # Близко к апексу
    }
]

# ==============================================================================
# 4. РАСЧЕТ ДИНАМИКИ СЕРДЕЧНОГО ЦИКЛА (КИНЕМАТИКА)
# ==============================================================================
frames_data = []

# Временная функция сердечного цикла (0 -> 1 -> 0: синусоидальное сокращение и расслабление)
t_steps = np.linspace(0, np.pi, N_FRAMES)
contraction_curve = np.sin(t_steps)  # 0 в начале, 1 на пике систолы, 0 в конце

print("Расчет деформаций миокарда и перемещения хорд...")

for f in range(N_FRAMES):
    act = contraction_curve[f]  # Текущий уровень активации систолы (0.0 - 1.0)
    
    # 1. Продольное укорочение (longitudinal shortening)
    # Базис смещается к стабильному апексу (z=0)
    z_f = Z_REF * (1.0 - LONGITUDINAL_SHORTENING * act * (Z_REF / H_BASE))
    
    # 2. Радиальное сужение с учетом региональной гетерогенности
    # Стенки устремляются к центральной оси
    r_f = R_REF * (1.0 - CONTRACTION_STRENGTH * act * regional_heterogeneity)
    
    # 3. Скручивание (Twist)
    # Апекс (z=0) и Базис (z=H_BASE) вращаются в противоположных направлениях
    # Пропорционально высоте z
    twist_angle = TWIST_STRENGTH * act * (Z_REF / H_BASE - 0.5)
    theta_f = THETA_REF + twist_angle
    
    # Перевод деформированных цилиндрических координат в декартовы (X, Y, Z)
    X_f = r_f * np.cos(theta_f)
    Y_f = r_f * np.sin(theta_f)
    Z_f = z_f
    
    # 4. Расчет региональной деформации (Strain-like показатель в %)
    # Рассчитаем как относительное изменение локального радиуса по сравнению с референсом
    # Т.к. модель кинематическая, выразим это через псевдо-strain (отрицательный при сжатии)
    strain_f = -((R_REF - r_f) / (R_REF + 1e-5)) * 100.0
    
    # 5. Расчет координат хорд для текущего кадра
    chords_coords = []
    for chord in chords_config:
        z1_idx, t1_idx = chord["p1"]
        z2_idx, t2_idx = chord["p2"]
        
        # Точки крепления хорды на деформируемой сетке ЛЖ
        p1_xyz = (X_f[z1_idx, t1_idx], Y_f[z1_idx, t1_idx], Z_f[z1_idx, t1_idx])
        p2_xyz = (X_f[z2_idx, t2_idx], Y_f[z2_idx, t2_idx], Z_f[z2_idx, t2_idx])
        
        chords_coords.append((p1_xyz, p2_xyz))
        
    frames_data.append({
        "X": X_f, "Y": Y_f, "Z": Z_f, 
        "strain": strain_f, 
        "chords": chords_coords
    })

# ==============================================================================
# 5. СБОРКА ИНТЕРАКТИВНОЙ 3D-СЦЕНЫ В PLOTLY
# ==============================================================================
print("Сборка интерактивной 3D сцены...")

# Стартовый кадр (Диастола, кадр 0)
init_frame = frames_data[0]

# Создаем базовые объекты геометрии ЛЖ
lv_surface = go.Surface(
    x=init_frame["X"], y=init_frame["Y"], z=init_frame["Z"],
    surfacecolor=init_frame["strain"],
    colorscale="YlOrRd",  # Градиент от желтого к красному для отображения деформации
    cmin=-40.0, cmax=0.0, # Диапазон деформации в %
    colorbar=dict(title="Regional Strain (%)", thickness=20, len=0.6),
    opacity=0.85,
    showscale=True,
    name="LV Endocardium"
)

# Собираем первоначальные линии для хорд
plot_data = [lv_surface]
for idx, chord in enumerate(chords_config):
    p1, p2 = init_frame["chords"][idx]
    chord_line = go.Scatter3d(
        x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]],
        mode="lines+markers",
        line=dict(color=chord["color"], width=6),
        marker=dict(size=4, color="white"),
        name=chord["name"]
    )
    plot_data.append(chord_line)

# Настройка анимационных кадров (Frames)
plotly_frames = []
for f in range(N_FRAMES):
    f_info = frames_data[f]
    
    # Обновление поверхности ЛЖ
    frame_traces = [
        go.Surface(
            x=f_info["X"], y=f_info["Y"], z=f_info["Z"],
            surfacecolor=f_info["strain"]
        )
    ]
    
    # Обновление каждой хорды
    for idx in range(len(chords_config)):
        p1, p2 = f_info["chords"][idx]
        frame_traces.append(
            go.Scatter3d(x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]])
        )
        
    plotly_frames.append(go.Frame(data=frame_traces, name=f"frame_{f}"))

# Настройка интерфейса, кнопок анимации и осей
layout = go.Layout(
    title=dict(
        text="3D Кинематическая модель ЛЖ с ложными хордами",
        x=0.5, font=dict(size=18, color="white")
    ),
    template="plotly_dark",
    scene=dict(
        xaxis=dict(title="X (cm)", range=[-3.5, 3.5], backgroundcolor="black", gridcolor="gray"),
        yaxis=dict(title="Y (cm)", range=[-3.5, 3.5], backgroundcolor="black", gridcolor="gray"),
        zaxis=dict(title="Z (cm)", range=[-0.5, 6.5], backgroundcolor="black", gridcolor="gray"),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=1.2) # Немного вытянем по оси Z для реалистичности ЛЖ
    ),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {
                "label": "▶ Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]
            },
            {
                "label": "⏸ Pause",
                "method": "animate",
                "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "x": 0.1, "xanchor": "right", "y": 0, "yanchor": "top"
    }],
    sliders=[{
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        # Удалили "position": "top", оставив только валидные параметры:
        "currentvalue": {"font": {"size": 14}, "prefix": "Кадр цикла: ", "visible": True},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [
            {
                "args": [[f"frame_{f}"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                "label": str(f),
                "method": "animate"
            } for f in range(N_FRAMES)
        ]
    }]
)

# Сборка финальной фигуры
fig = go.Figure(data=plot_data, layout=layout, frames=plotly_frames)

# ==============================================================================
# 6. ЭКСПОРТ РЕЗУЛЬТАТА И ИНФОРМАЦИОННЫЙ ВЫВОД
# ==============================================================================
output_filename = "lv_mechanics_model.html"
current_directory = os.getcwd()
full_path = os.path.join(current_directory, output_filename)

print(f"Сохранение интерактивной 3D модели в автономный HTML...")
fig.write_html(full_path, auto_play=False, include_plotlyjs="cdn")

print("\n" + "="*80)
print("СТАТУС ВЫПОЛНЕНИЯ: УСПЕШНО")
print(f"Рабочая директория скрипта: {current_directory}")
print(f"Файл с 3D-анимацией сохранен по пути:")
print(f"--> {full_path}")
print("="*80)
print("ИНСТРУКЦИЯ: Откройте этот .html файл в любом веб-браузере (Chrome, Edge, Safari).")
print("Используйте мышь для вращения ЛЖ в 3D пространстве и нажмите кнопку 'Play' для запуска цикла.")
print("="*80 + "\n")