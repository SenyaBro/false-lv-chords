# false-lv-chords

Исследовательский репозиторий для диссертационного проекта по физиологии, посвящённого изучению **ложных хорд левого желудочка сердца** и их возможной связи с механикой миокарда, геометрией ЛЖ, функциональными показателями и ЭКГ.

Проект ориентирован не на простое сравнение «есть хорда / нет хорды», а на анализ **механического фенотипа ложных хорд** и поиск ответа на более фундаментальный вопрос:

> Какой биологический смысл имеют ложные хорды левого желудочка?

Возможные интерпретации, которые проверяются в проекте:

- ложные хорды как анатомический вариант нормы;
- ложные хорды как внутренние механические ограничения ЛЖ;
- ложные хорды как топологическая связь между сегментами ЛЖ;
- ложные хорды как модификатор региональной механики миокарда;
- ложные хорды как фактор, связанный с геометрией, функцией или ЭКГ;
- ложные хорды как фенотип без клинически значимого эффекта.

---

## 1. Научная логика проекта

Основной акцент делается на **региональной механике**, а не только на глобальной функции сердца.

Ключевые исследовательские направления:

1. Описание анатомического и механического фенотипа ложных хорд.
2. Анализ связи ложных хорд с глобальной геометрией ЛЖ.
3. Анализ связи ложных хорд с функциональными параметрами сердца.
4. Анализ связи ложных хорд с ЭКГ-показателями.
5. Анализ связи ложных хорд с параметрами strain / speckle tracking.
6. Поиск локальной механической подписи:
   - зоны прикрепления хорды;
   - соседние сегменты;
   - удалённые сегменты.
7. Проверка spatial gradient эффекта:
   - insertion zone;
   - adjacent zone;
   - remote zone.
8. Топологическое представление хорды как связи между сегментами ЛЖ.
9. Проверка устойчивости результатов:
   - bootstrap;
   - stability selection;
   - FDR;
   - sensitivity analysis;
   - Elastic Net;
   - sparse PLS;
   - Bayesian shrinkage для выбранных гипотез.

---

## 2. Расположение проекта и данных

Планируемое расположение проекта на локальной машине:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res
```

Основной исходный аналитический датасет:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res\data\final_analysis_dataset.xlsx
```

Внутри репозитория данные должны быть организованы так:

```text
data/
├─ raw/          # исходные данные, не изменяются вручную
├─ interim/      # промежуточные очищенные данные
├─ processed/    # финальные аналитические версии датасетов
└─ README.md     # описание структуры данных
```

Важно:

- `data/raw/` не должен коммититься в Git;
- персональные данные не должны попадать в публичные файлы;
- исходные Excel-файлы используются только как вход для воспроизводимого пайплайна;
- финальные версии датасета сохраняются в `data/processed/`;
- информация о версиях датасетов фиксируется в `data/processed/manifest.csv`.

---

## 3. Структура проекта

```text
false-lv-chords/
├─ GEMINI.md
├─ .aiexclude
├─ .gitignore
├─ README.md
├─ pyproject.toml
├─ uv.lock
├─ .python-version
├─ .env.example
├─ Makefile
├─ dvc.yaml
├─ params.yaml
├─ Dockerfile
├─ .dockerignore
├─ docker-compose.yml
│
├─ .github/
│  └─ workflows/
│     └─ ci.yml
│
├─ docs/
│  ├─ PROJECT_BRIEF.md
│  ├─ SCIENTIFIC_FRAMEWORK.md
│  ├─ ANALYSIS_PLAN.md
│  ├─ STATISTICAL_GUARDRAILS.md
│  ├─ VARIABLE_DICTIONARY.md
│  ├─ DATA_PROVENANCE.md
│  ├─ PUBLICATION_STRATEGY.md
│  └─ PROMPT_PROTOCOLS.md
│
├─ data/
│  ├─ raw/
│  ├─ interim/
│  ├─ processed/
│  └─ README.md
│
├─ notebooks/
│  ├─ 00_data_audit.ipynb
│  ├─ 01_feature_engineering.ipynb
│  ├─ 02_mechanics_geometry_ecg.ipynb
│  ├─ 03_spatial_topology.ipynb
│  ├─ 04_modeling_stability.ipynb
│  └─ 05_manuscript_figures.ipynb
│
├─ src/
│  └─ false_chords/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ data_schema.py
│     ├─ validation.py
│     ├─ features.py
│     ├─ spatial_topology.py
│     ├─ models.py
│     ├─ stability.py
│     ├─ visualization.py
│     └─ reporting.py
│
├─ scripts/
│  ├─ setup_project.sh
│  ├─ validate_data.py
│  ├─ build_dataset.py
│  ├─ train_model.py
│  ├─ run_bootstrap.py
│  ├─ export_tables.py
│  └─ export_figures.py
│
├─ tests/
│  ├─ test_data_schema.py
│  ├─ test_validation.py
│  ├─ test_features.py
│  ├─ test_spatial_topology.py
│  ├─ test_models.py
│  └─ test_stability.py
│
├─ models/
│  ├─ README.md
│  ├─ baseline/
│  ├─ elastic_net/
│  ├─ sparse_pls/
│  └─ bayesian/
│
├─ outputs/
│  ├─ reports/
│  ├─ tables/
│  ├─ figures/
│  └─ diagnostics/
│
├─ mlruns/
│
└─ references/
   ├─ papers/
   ├─ guidelines/
   └─ notes/
```

---

## 4. Назначение основных директорий

### `docs/`

Научная и методологическая документация проекта.

Ключевые файлы:

- `PROJECT_BRIEF.md` — краткое описание проекта;
- `SCIENTIFIC_FRAMEWORK.md` — научная концепция, гипотезы, механистическая логика;
- `ANALYSIS_PLAN.md` — план анализа данных;
- `STATISTICAL_GUARDRAILS.md` — статистические ограничения и защита от p-hacking;
- `VARIABLE_DICTIONARY.md` — словарь переменных;
- `DATA_PROVENANCE.md` — происхождение данных и версионность;
- `PUBLICATION_STRATEGY.md` — логика будущей статьи / главы диссертации;
- `PROMPT_PROTOCOLS.md` — правила постановки задач AI-агентам.

### `data/`

Данные проекта.

- `raw/` — исходные файлы;
- `interim/` — промежуточные данные после первичной очистки;
- `processed/` — финальные аналитические датасеты;
- `manifest.csv` — журнал версий обработанных датасетов.

### `notebooks/`

Ноутбуки для прозрачного анализа и визуальной проверки результатов.

Логика ноутбуков:

- `00_data_audit.ipynb` — аудит данных;
- `01_feature_engineering.ipynb` — построение признаков;
- `02_mechanics_geometry_ecg.ipynb` — анализ механики, геометрии, функции и ЭКГ;
- `03_spatial_topology.ipynb` — региональный и топологический анализ;
- `04_modeling_stability.ipynb` — модели, bootstrap, stability selection;
- `05_manuscript_figures.ipynb` — финальные рисунки для статьи / диссертации.

### `src/false_chords/`

Основной Python-пакет проекта.

Важно: файл инициализации пакета должен называться:

```text
__init__.py
```

а не:

```text
init.py
```

### `scripts/`

Скрипты для запуска отдельных этапов анализа из командной строки.

### `tests/`

Тесты для проверки корректности схемы данных, валидации, генерации признаков, топологической логики и моделей.

### `models/`

Сохранённые модели и модельные артефакты.

Основные поддиректории:

- `baseline/`;
- `elastic_net/`;
- `sparse_pls/`;
- `bayesian/`.

### `outputs/`

Все результаты анализа.

- `outputs/reports/` — текстовые отчёты;
- `outputs/tables/` — таблицы;
- `outputs/figures/` — графики;
- `outputs/diagnostics/` — диагностические отчёты, манифесты, логи.

### `references/`

Литература, клинические рекомендации, методические материалы и заметки.

---

## 5. Установка окружения

Проект рассчитан на Python и управление зависимостями через `uv`.

### 5.1. Установить `uv`

Если `uv` ещё не установлен:

```bash
pip install uv
```

или через официальный способ установки `uv`, если он уже используется в системе.

### 5.2. Перейти в папку проекта

```bash
cd C:\Users\Ars\projects\university\lab_urfu_2026\fh_res
```

### 5.3. Создать окружение и установить зависимости

```bash
uv sync
```

Если используется `.python-version`, убедиться, что активна нужная версия Python.

Проверить Python:

```bash
python --version
```

### 5.4. Активировать окружение

На Windows:

```bash
.venv\Scripts\activate
```

На Linux / macOS:

```bash
source .venv/bin/activate
```

### 5.5. Проверить установку

```bash
python -c "import false_chords; print('false_chords package is available')"
```

---

## 6. Настройка переменных окружения

Создать локальный `.env` на основе шаблона:

```bash
copy .env.example .env
```

или для Linux / macOS:

```bash
cp .env.example .env
```

Файл `.env` не должен коммититься в Git.

В `.env` могут храниться:

```text
PROJECT_ROOT
DATA_DIR
RAW_DATA_DIR
PROCESSED_DATA_DIR
MLFLOW_TRACKING_URI
```

---

## 7. Как запустить анализ

Анализ должен запускаться воспроизводимо: через `Makefile`, `scripts/` или DVC pipeline.

### 7.1. Проверка данных

```bash
make validate-data
```

или напрямую:

```bash
python scripts/validate_data.py
```

Ожидаемые результаты:

```text
outputs/diagnostics/data_validation_report.md
outputs/tables/variable_type_audit.xlsx
outputs/tables/missingness_summary.xlsx
```

### 7.2. Сборка аналитического датасета

```bash
make build-dataset
```

или:

```bash
python scripts/build_dataset.py
```

Ожидаемые результаты:

```text
data/processed/dataset_v0.1.parquet
data/processed/manifest.csv
outputs/diagnostics/build_dataset_manifest.json
```

### 7.3. Запуск базового анализа

```bash
make model-baseline
```

или:

```bash
python scripts/train_model.py
```

Ожидаемые результаты:

```text
outputs/tables/baseline_model_results.xlsx
outputs/figures/baseline_model_coefficients.png
outputs/diagnostics/model_run_manifest.json
```

### 7.4. Запуск bootstrap / stability analysis

```bash
make bootstrap
```

или:

```bash
python scripts/run_bootstrap.py
```

Ожидаемые результаты:

```text
outputs/tables/bootstrap_results.xlsx
outputs/tables/selection_frequency.xlsx
outputs/figures/bootstrap_stability_plot.png
```

### 7.5. Экспорт таблиц

```bash
make tables
```

или:

```bash
python scripts/export_tables.py
```

### 7.6. Экспорт рисунков

```bash
make figures
```

или:

```bash
python scripts/export_figures.py
```

### 7.7. Полный запуск пайплайна

Когда все этапы будут настроены:

```bash
make all
```

или через DVC:

```bash
dvc repro
```

---

## 8. Основные выходные результаты

Результаты анализа сохраняются в `outputs/`.

Примерная структура:

```text
outputs/
├─ reports/
│  ├─ data_audit_report.md
│  ├─ statistical_analysis_report.md
│  └─ manuscript_summary.md
│
├─ tables/
│  ├─ descriptive_statistics.xlsx
│  ├─ missingness_summary.xlsx
│  ├─ pca_loadings.xlsx
│  ├─ baseline_model_results.xlsx
│  ├─ elastic_net_selection_frequency.xlsx
│  ├─ bootstrap_results.xlsx
│  └─ fdr_corrected_results.xlsx
│
├─ figures/
│  ├─ missingness_heatmap.png
│  ├─ domain_correlation_heatmap.png
│  ├─ pca_explained_variance.png
│  ├─ spatial_gradient_plot.png
│  ├─ regional_mechanics_contrast.png
│  └─ stability_selection_plot.png
│
└─ diagnostics/
   ├─ run_manifest.json
   ├─ data_validation_report.md
   └─ model_diagnostics.md
```

---

## 9. Проверка качества кода

Запуск тестов:

```bash
make test
```

или:

```bash
pytest
```

Проверка форматирования и статического анализа, если настроено:

```bash
make lint
```

---

## 10. Работа с MLflow

MLflow используется для фиксации запусков моделей, параметров, метрик и артефактов.

Локальный запуск UI:

```bash
mlflow ui
```

По умолчанию результаты MLflow могут сохраняться в:

```text
mlruns/
```

В Git и AI-индексацию содержимое `mlruns/` обычно не включается.

---

## 11. Работа с DVC

DVC используется для воспроизводимого запуска этапов обработки данных и анализа.

Основные команды:

```bash
dvc status
dvc repro
dvc dag
```

Файл `dvc.yaml` должен описывать ключевые этапы:

```text
validate_data
build_dataset
feature_engineering
modeling
bootstrap
export_tables
export_figures
```

---

## 12. Безопасность данных

Проект содержит биомедицинские данные, поэтому необходимо соблюдать правила:

- не коммитить `data/raw/`;
- не коммитить `.env`;
- не публиковать персональные данные;
- не выводить ФИО и идентификаторы в логи;
- не использовать персональные данные в демонстрационных примерах;
- не передавать исходные таблицы AI-агентам без явного решения пользователя;
- не использовать сырые данные как контекст для AI-индексации.

Для этого используется файл:

```text
.aiexclude
```

Он исключает из индексации:

```text
raw data
personal data
.env
models
mlruns
large tables
temporary files
generated outputs
```

---

## 13. Работа с AI-агентами

Основные правила для AI-агентов описаны в:

```text
GEMINI.md
```

Дополнительные протоколы постановки задач:

```text
docs/PROMPT_PROTOCOLS.md
```

AI-агент должен:

- не индексировать сырые и персональные данные;
- не придумывать названия переменных;
- не придумывать результаты анализа;
- сначала проверять структуру данных;
- сохранять научную логику проекта;
- различать ковариаты, медиаторы, предикторы и исходы;
- не превращать проект в «поиск значимых p-value»;
- интерпретировать результаты физиологически.

---

## 14. Минимальный рабочий сценарий

После первичной настройки проекта типовой сценарий работы выглядит так:

```bash
cd C:\Users\Ars\projects\university\lab_urfu_2026\fh_res

uv sync

make validate-data
make build-dataset
make model-baseline
make bootstrap
make tables
make figures
```

После этого результаты будут находиться в:

```text
outputs/
```

---

## 15. Текущий статус проекта

На текущем этапе проект находится в стадии структурирования исследовательского репозитория и подготовки воспроизводимого аналитического контура.

Приоритетные ближайшие задачи:

1. Зафиксировать структуру репозитория.
2. Создать документацию в `docs/`.
3. Настроить `.aiexclude`, `.gitignore`, `pyproject.toml`.
4. Описать переменные и домены.
5. Подготовить `params.yaml`.
6. Реализовать первичный аудит данных.
7. Реализовать сборку аналитического датасета.
8. Перейти к feature engineering для региональной и топологической логики.
