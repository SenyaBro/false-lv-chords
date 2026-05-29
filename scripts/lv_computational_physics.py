import os
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# 1. ПАРАМЕТРЫ ФИЗИЧЕСКОЙ СИСТЕМЫ И ЧИСЛЕННОГО ИНТЕГРИРОВАНИЯ
# ==============================================================================
N_THETA = 24          # Точки по окружности
N_Z = 12              # Точки по высоте
DT = 0.01             # Шаг интегрирования по времени (секунды)
STEPS = 150           # Всего шагов расчета (фаза систолы)

# Физические свойства миокарда
M_NODE = 0.05         # Масса узла сетки (кг)
K_PASSIVE = 150.0     # Жесткость пассивной ткани миокарда (Н/м)
B_DAMPING = 1.5       # Коэффициент вязкого затухания ткани
F_ACTIVE_MAX = 8.0    # Максимальная сила сокращения волокон

# Физические свойства ложной хорды
K_CHORD = 350.0       # Высокая жесткость хорды (Н/м) -> симулируем фиброзный тяж

H_BASE = 5.0
R_BASE = 2.0

print("Запуск численного FSI/Structural-прототипа левого желудочка...")

# ==============================================================================
# 2. ИНИЦИАЛИЗАЦИЯ И ТОПОЛОГИЯ СВЯЗЕЙ (МАТРИЦА СМЕЖНОСТИ)
# ==============================================================================
z_vals = np.linspace(0.1, H_BASE, N_Z)
theta_vals = np.linspace(0, 2 * np.pi, N_THETA, endpoint=False)

# Создаем начальные 3D координаты узлов (референсная диастола)
X_init, Y_init, Z_init = [], [], []
for z in z_vals:
    r = R_BASE * np.sqrt(1 - ((H_BASE - z) / H_BASE) ** 2)
    for t in theta_vals:
        X_init.append(r * np.cos(t))
        Y_init.append(r * np.sin(t))
        Z_init.append(z)

pos = np.stack([X_init, Y_init, Z_init], axis=1) # Массив положений [N_nodes x 3]
n_nodes = len(pos)

vel = np.zeros_like(pos) # Скорости узлов (изначально покой)

# Генерируем внутренние структурные связи миокарда (пружины)
# Каждая точка связана с соседом по Z и по окружности THETA
springs = []
def get_idx(z_i, t_i):
    return z_i * N_THETA + (t_i % N_THETA)

for zi in range(N_Z):
    for ti in range(N_THETA):
        curr = get_idx(zi, ti)
        # Связь по горизонтали (окружность)
        springs.append((curr, get_idx(zi, ti + 1), K_PASSIVE))
        # Связь по вертикали (продольные волокна)
        if zi < N_Z - 1:
            springs.append((curr, get_idx(zi + 1, ti), K_PASSIVE * 1.5)) # вдоль волокон жесткость выше

# Вычисляем длины покоя пружин (L0) в диастолу
springs_L0 = [np.linalg.norm(pos[p1] - pos[p2]) for p1, p2, k in springs]

# Задаем ложную хорду: крепим между противоположными стенками на среднем уровне (Mid-LV)
chord_node1 = get_idx(int(N_Z * 0.5), 0)
chord_node2 = get_idx(int(N_Z * 0.5), int(N_THETA * 0.5))
chord_L0 = np.linalg.norm(pos[chord_node1] - pos[chord_node2]) # Длина покоя хорды

# ==============================================================================
# 3. ЦИКЛ ЧИСЛЕННОГО ИНТЕГРИРОВАНИЯ ДИНАМИКИ СИСТЕМЫ (МЕТОД ЭЙЛЕРА-КРОМЕРА)
# ==============================================================================
history = [pos.copy()] # Сюда сохраняем кадры для анимации

for step in range(STEPS):
    # Текущая фаза активации систолы (плавное нарастание силы мышц)
    activation = np.sin((step / STEPS) * np.pi)
    
    # Сброс вектора результирующих сил для каждого узла
    forces = np.zeros_like(pos)
    
    # А. Расчет внутренних пассивных сил упругости ткани (Закон Гука)
    for idx, (p1, p2, k_spring) in enumerate(springs):
        vec = pos[p2] - pos[p1]
        L = np.linalg.norm(vec)
        if L == 0: continue
        direction = vec / L
        # Сила упругости пружины
        f_mag = k_spring * (L - springs_L0[idx])
        forces[p1] += f_mag * direction
        forces[p2] -= f_mag * direction
        
    # Б. Расчет активных сил миокарда (Имитация активного сжатия и твиста)
    for zi in range(N_Z):
        for ti in range(N_THETA):
            idx = get_idx(zi, ti)
            # Вектор силы устремлен к центру оси ЛЖ + тангенциальный сдвиг для Twist
            r_vec = np.array([-pos[idx, 0], -pos[idx, 1], 0])
            r_len = np.linalg.norm(r_vec)
            if r_len > 0:
                # Направление радиального сжатия
                dir_contract = r_vec / r_len
                # Тангенциальное направление (ротация)
                dir_twist = np.array([-pos[idx, 1], pos[idx, 0], 0])
                dir_twist /= np.linalg.norm(dir_twist)
                
                # Сила закручивания зависит от высоты Z (апекс в одну сторону, базис - в другую)
                z_factor = (pos[idx, 2] / H_BASE) - 0.35
                
                # Суммарный вектор активного сокращения волокна миокарда
                f_act = (dir_contract * 1.0 + dir_twist * z_factor * 1.5) * F_ACTIVE_MAX * activation
                forces[idx] += f_act

    # В. РАСЧЕТ СИЛЫ НА ТЯЖЕНИЯ ЛОЖНОЙ ХОРДЫ (Constraint)
    vec_chord = pos[chord_node2] - pos[chord_node1]
    L_chord_curr = np.linalg.norm(vec_chord)
    if L_chord_curr > chord_L0: # Хорда натянулась!
        dir_chord = vec_chord / L_chord_curr
        # Сила сопротивления жесткой нити
        f_chord_mag = K_CHORD * (L_chord_curr - chord_L0)
        forces[chord_node1] += f_chord_mag * dir_chord
        forces[chord_node2] -= f_chord_mag * dir_chord

    # Г. Вязкое демпфирование ткани (чтобы система не шла в разнос)
    forces -= B_DAMPING * vel

    # Д. Шаг численного интегрирования Ньютона-Эйлера
    # Ускорение: a = F / m
    acc = forces / M_NODE
    # Скорость: v_new = v_old + a * dt
    vel += acc * DT
    # Положение: x_new = x_old + v_new * dt
    pos += vel * DT
    
    # Фиксируем верхнее кольцо (базис), чтобы сердце не улетало в космос от сил
    for ti in range(N_THETA):
        base_idx = get_idx(N_Z - 1, ti)
        pos[base_idx, 2] = H_BASE # жестко держим высоту базиса
    
    # Сохраняем каждый 5-й шаг для гладкой 3D визуализации
    if step % 5 == 0:
        history.append(pos.copy())

# ==============================================================================
# 4. СБОРКА РЕЗУЛЬТАТОВ В ИНТЕРАКТИВНУЮ СЦЕНУ PLOTLY
# ==============================================================================
print("Расчет завершен. Идет рендеринг физических полей...")

init_pos = history[0]

# Строим сетку треугольников для отрисовки честной поверхности ЛЖ через Mesh3d
i_tri, j_tri, k_tri = [], [], []
for zi in range(N_Z - 1):
    for ti in range(N_THETA):
        p0 = get_idx(zi, ti)
        p1 = get_idx(zi, ti + 1)
        p2 = get_idx(zi + 1, ti)
        p3 = get_idx(zi + 1, ti + 1)
        # Два треугольника на полигон сетки
        i_tri.extend([p0, p1])
        j_tri.extend([p1, p3])
        k_tri.extend([p2, p2])

# Псевдо-strain для визуализации: рассчитываем смещение каждой точки от исходной
def get_displacement_color(curr_pos):
    return -np.linalg.norm(curr_pos - init_pos, axis=1) * 10.0

lv_mesh = go.Mesh3d(
    x=init_pos[:, 0], y=init_pos[:, 1], z=init_pos[:, 2],
    i=i_tri, j=j_tri, k=k_tri,
    intensity=get_displacement_color(init_pos),
    colorscale="Viridis", cmin=-15.0, cmax=0.0,
    colorbar=dict(title="Локальное смещение ткани (у.е.)", thickness=20),
    opacity=0.9, name="Миокард ЛЖ"
)

# Отрисовка ложной хорды
p1_c, p2_c = init_pos[chord_node1], init_pos[chord_node2]
chord_line = go.Scatter3d(
    x=[p1_c[0], p2_c[0]], y=[p1_c[1], p2_c[1]], z=[p1_c[2], p2_c[2]],
    mode="lines+markers", line=dict(color="#FF0055", width=8),
    marker=dict(size=6, color="white"), name="Ложная хорда (Жесткая)"
)

# Сборка кадров анимации
plotly_frames = []
for f_pos in history:
    plotly_frames.append(go.Frame(data=[
        go.Mesh3d(x=f_pos[:, 0], y=f_pos[:, 1], z=f_pos[:, 2], intensity=get_displacement_color(f_pos)),
        go.Scatter3d(x=[f_pos[chord_node1, 0], f_pos[chord_node2, 0]], 
                     y=[f_pos[chord_node1, 1], f_pos[chord_node2, 1]], 
                     z=[f_pos[chord_node1, 2], f_pos[chord_node2, 2]])
    ]))

layout = go.Layout(
    template="plotly_dark",
    scene=dict(
        xaxis=dict(range=[-2.5, 2.5], gridcolor="#222"),
        yaxis=dict(range=[-2.5, 2.5], gridcolor="#222"),
        zaxis=dict(range=[-0.2, 5.5], gridcolor="#222"),
        aspectratio=dict(x=1, y=1, z=1.2)
    ),
    updatemenus=[{
        "type": "buttons", "direction": "left", "pad": {"r": 10, "t": 85},
        "buttons": [
            {"label": "▶ Запустить расчет", "method": "animate", "args": [None, {"frame": {"duration": 60, "redraw": True}, "fromcurrent": True}]},
            {"label": "⏸ Пауза", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ], "x": 0.1, "y": 0
    }]
)

fig = go.Figure(data=[lv_mesh, chord_line], layout=layout, frames=plotly_frames)

output_path = os.path.join(os.getcwd(), "lv_computational_physics.html")
fig.write_html(output_path, auto_play=False, include_plotlyjs="cdn")
print(f"\n[ДОКТОРСКАЯ ПО МАТЕМАТИКЕ] Динамический прототип готов:\n--> {output_path}\n")