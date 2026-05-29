import json
from pathlib import Path

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Расчёт систолического напряжения стенки левого желудочка (Grossman formula)\n",
    "\n",
    "Этот ноутбук содержит код для расчёта **систолического напряжения стенки левого желудочка (г/см²)** и его интеграции в датасет `final_analysis_dataset_ver2.xlsx`.\n",
    "\n",
    "### Формула Гроссмана:\n",
    "$$\\sigma = 0.334 \\times \\frac{P \\times d}{h \\times (1 + \\frac{h}{d})}$$\n",
    "Где:\n",
    "- $P$ — систолическое давление (`exercise_peak_systolic_bp_mmhg` / САД НАГР)\n",
    "- $d$ — конечно-систолический размер ЛЖ (`echo_lv_end_systolic_diameter_mm` / КСР)\n",
    "- $h$ — толщина задней стенки левого желудочка в систолу (`echo_lv_posterior_wall_thickness_mm` / ЗС)\n",
    "\n",
    "### Важный научный нюанс:\n",
    "В исходном датасете столбец `echo_lv_posterior_wall_thickness_mm` (ЗС) заполнен только для 15 пациентов. При этом эти 15 пациентов **не пересекаются** с 66 пациентами, прошедшими нагрузочные тесты (для которых заполнено давление `exercise_peak_systolic_bp_mmhg`). Из-за этого прямой расчёт «в лоб» даёт 0 заполненных значений.\n",
    "\n",
    "Тем не менее, в датасете присутствует расчетный показатель относительной толщины стенки — `echo_lv_relative_wall_thickness_ratio` (ОТС / RWT), который рассчитывается по формуле:\n",
    "$$RWT = \\frac{2 \\times LVPW}{LVEDd}$$\n",
    "Это позволяет нам **математически восстановить** толщину задней стенки ($LVPW$ / $h$) для остальных пациентов, у которых заполнены RWT и LVEDd:\n",
    "$$h = \\frac{RWT \\times LVEDd}{2}$$\n",
    "\n",
    "Благодаря этому методу мы получаем **64 успешно рассчитанных значения** систолического напряжения стенки ЛЖ!"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "from pathlib import Path\n",
    "\n",
    "# Пути к файлам\n",
    "DATASET_PATH = Path('../data/final_analysis_dataset_ver2.xlsx')\n",
    "if not DATASET_PATH.exists():\n",
    "    DATASET_PATH = Path('data/final_analysis_dataset_ver2.xlsx')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Загрузка датасета\n",
    "df = pd.read_excel(DATASET_PATH)\n",
    "print(\"Размерность датасета до добавления колонки:\", df.shape)\n",
    "print(\"Количество непустых значений до восстановления:\")\n",
    "print(\"  САД нагрузки (exercise_peak_systolic_bp_mmhg):\", df['exercise_peak_systolic_bp_mmhg'].notna().sum())\n",
    "print(\"  КСР (echo_lv_end_systolic_diameter_mm):       \", df['echo_lv_end_systolic_diameter_mm'].notna().sum())\n",
    "print(\"  ЗС (echo_lv_posterior_wall_thickness_mm):     \", df['echo_lv_posterior_wall_thickness_mm'].notna().sum())\n",
    "print(\"  ОТС (echo_lv_relative_wall_thickness_ratio):  \", df['echo_lv_relative_wall_thickness_ratio'].notna().sum())\n",
    "print(\"  КДР (echo_lv_end_diastolic_diameter_mm):      \", df['echo_lv_end_diastolic_diameter_mm'].notna().sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Восстановление толщины задней стенки (h) через RWT и LVEDd для пропущенных значений\n",
    "reconstructed_h = df['echo_lv_relative_wall_thickness_ratio'] * df['echo_lv_end_diastolic_diameter_mm'] / 2\n",
    "\n",
    "# Заполняем пропуски в ЗС восстановленными значениями\n",
    "df['echo_lv_posterior_wall_thickness_mm'] = df['echo_lv_posterior_wall_thickness_mm'].fillna(reconstructed_h)\n",
    "print(\"Количество непустых значений ЗС после восстановления:\", df['echo_lv_posterior_wall_thickness_mm'].notna().sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Выделение переменных для расчёта\n",
    "P = df['exercise_peak_systolic_bp_mmhg']\n",
    "d = df['echo_lv_end_systolic_diameter_mm']\n",
    "h = df['echo_lv_posterior_wall_thickness_mm']\n",
    "\n",
    "# Расчёт систолического напряжения стенки ЛЖ по формуле Гроссмана\n",
    "df['echo_lv_systolic_wall_stress_g_cm2'] = 0.334 * P * d / (h * (1 + (h / d)))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Оценка результатов\n",
    "print(\"Размерность датасета после расчёта:\", df.shape)\n",
    "print(\"Количество успешно рассчитанных значений напряжения стенки:\", df['echo_lv_systolic_wall_stress_g_cm2'].notna().sum())\n",
    "print(\"\\nОписательная статистика новой переменной:\")\n",
    "print(df['echo_lv_systolic_wall_stress_g_cm2'].describe())\n",
    "print(\"\\nПервые 10 строк с рассчитанными значениями:\")\n",
    "cols_show = ['subject_full_name', 'exercise_peak_systolic_bp_mmhg', 'echo_lv_end_systolic_diameter_mm', 'echo_lv_posterior_wall_thickness_mm', 'echo_lv_systolic_wall_stress_g_cm2']\n",
    "print(df[cols_show].dropna().head(10))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Сохранение датасета\n",
    "df.to_excel(DATASET_PATH, index=False)\n",
    "print(\"Обновлённый датасет успешно сохранён по пути:\", DATASET_PATH)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

notebook_path = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\notebooks\11_calculate_systolic_wall_stress.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1, ensure_ascii=False)

print("Updated Jupyter notebook created successfully!")
