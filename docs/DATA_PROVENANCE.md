# DATA_PROVENANCE.md

# Происхождение, версии и трассируемость данных проекта `false-lv-chords`

## 1. Назначение документа

Этот документ фиксирует происхождение данных, структуру батчей, версии аналитических датасетов и изменения между ними.

Его задача — обеспечить воспроизводимость исследования:

```text
откуда взяты данные
когда они добавлены
какие файлы входят в каждый batch
какие пациенты включены
какие пациенты исключены
какие переменные включены
какие переменные исключены
что изменилось между версиями dataset
какой код использовался для сборки dataset
какие outputs соответствуют какой версии данных
```

Этот файл должен обновляться каждый раз, когда:

- добавлен новый batch данных;
- изменился исходный Excel-файл;
- изменились правила очистки;
- изменился словарь переменных;
- изменились критерии включения/исключения;
- создана новая версия `dataset_vX.Y`;
- исправлена ошибка в данных;
- удалены или добавлены переменные;
- пересобраны результаты анализа.

---

## 2. Основное расположение данных

Планируемый корень проекта:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res
```

Основной исходный аналитический файл на старте проекта:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res\data\final_analysis_dataset.xlsx
```

Рабочая структура данных внутри репозитория:

```text
data/
├─ raw/
│  ├─ batch_2026-05-10/
│  │  ├─ echo.xlsx
│  │  ├─ ecg.xlsx
│  │  └─ metadata.yaml
│  └─ batch_YYYY-MM-DD/
│     └─ metadata.yaml
│
├─ interim/
│
├─ processed/
│  ├─ dataset_v0.1.parquet
│  ├─ dataset_v0.2.parquet
│  └─ manifest.csv
│
└─ README.md
```

Основной принцип:

```text
data/raw/ не изменяется вручную
```

Все изменения должны происходить через код и фиксироваться в `data/processed/manifest.csv` и в этом документе.

---

## 3. Уровни данных

В проекте используются три уровня данных.

## 3.1. Raw data

Папка:

```text
data/raw/
```

Назначение:

```text
исходные файлы, полученные из приборов, таблиц, ручного ввода или объединённых источников
```

Правила:

- не изменять вручную;
- не перезаписывать;
- не коммитить в публичный Git;
- не передавать AI-агентам как индексируемый контекст;
- хранить рядом `metadata.yaml`;
- фиксировать дату получения;
- фиксировать источник;
- фиксировать ответственного за добавление.

## 3.2. Interim data

Папка:

```text
data/interim/
```

Назначение:

```text
промежуточные данные после первичной очистки, нормализации названий, объединения таблиц
```

Примеры:

```text
standardized_columns.parquet
merged_echo_ecg.parquet
validated_subjects.parquet
features_intermediate.parquet
```

Правила:

- могут быть пересобраны из raw data;
- не являются финальной аналитической версией;
- должны иметь связанный manifest или log;
- не должны содержать лишние персональные идентификаторы.

## 3.3. Processed data

Папка:

```text
data/processed/
```

Назначение:

```text
финальные аналитические версии dataset
```

Примеры:

```text
dataset_v0.1.parquet
dataset_v0.2.parquet
dataset_v1.0.parquet
manifest.csv
```

Правила:

- каждая версия должна быть воспроизводима;
- каждая версия должна иметь запись в `manifest.csv`;
- каждая версия должна иметь описание изменений;
- каждая версия должна быть связана с конкретной версией кода / параметров;
- результаты анализа должны ссылаться на конкретную версию dataset.

---

## 4. Batch logic

Каждое поступление данных оформляется как отдельный batch.

Пример:

```text
data/raw/batch_2026-05-10/
├─ echo.xlsx
├─ ecg.xlsx
└─ metadata.yaml
```

## 4.1. Название batch

Формат:

```text
batch_YYYY-MM-DD
```

Примеры:

```text
batch_2026-05-10
batch_2026-06-01
batch_2026-07-15
```

Если в один день добавлено несколько независимых batch, использовать суффикс:

```text
batch_2026-05-10_a
batch_2026-05-10_b
```

## 4.2. Обязательный metadata.yaml для batch

Каждый batch должен иметь файл:

```text
metadata.yaml
```

Рекомендуемый шаблон:

```yaml
batch_id: batch_2026-05-10
date_added: 2026-05-10
added_by: "Ars"
source_type: "manual_export"
source_description: "Initial combined echo/ECG dataset for false LV chord project"
files:
  - file_name: echo.xlsx
    file_type: "echocardiography"
    description: "Echo and strain-related variables"
    original_source: "local clinical/research table"
    contains_personal_data: true
  - file_name: ecg.xlsx
    file_type: "ecg"
    description: "ECG variables"
    original_source: "local clinical/research table"
    contains_personal_data: true
expected_subjects: null
expected_variables: null
notes:
  - "Raw files must not be edited manually."
  - "Personal identifiers must be removed before processed dataset creation."
```

## 4.3. Batch registry

Каждый batch должен быть добавлен в таблицу ниже.

| Batch ID | Date added | Source files | Data type | Expected n | Expected p | Status | Notes |
|---|---:|---|---|---:|---:|---|---|
| batch_2026-05-10 | 2026-05-10 | final_analysis_dataset.xlsx / echo.xlsx / ecg.xlsx | echo + ECG + metadata | ≈200 | ≈240 | planned / initial | Initial project dataset. Exact structure must be confirmed by data audit. |

---

## 5. Source files registry

Эта таблица фиксирует исходные файлы.

| File ID | Batch ID | File path | File type | Description | Contains personal data | Status |
|---|---|---|---|---|---|---|
| source_001 | batch_2026-05-10 | data/final_analysis_dataset.xlsx | Excel | Initial analytical dataset with echo, chord, strain, ECG and related variables | yes / unknown | to audit |
| source_002 | batch_2026-05-10 | data/raw/batch_2026-05-10/echo.xlsx | Excel | Echocardiography-related source file | yes / unknown | planned |
| source_003 | batch_2026-05-10 | data/raw/batch_2026-05-10/ecg.xlsx | Excel | ECG-related source file | yes / unknown | planned |

Status values:

```text
planned
received
to audit
audited
excluded
archived
superseded
```

---

## 6. Dataset versioning

Финальные аналитические датасеты должны иметь версии.

Формат:

```text
dataset_vMAJOR.MINOR.parquet
```

Примеры:

```text
dataset_v0.1.parquet
dataset_v0.2.parquet
dataset_v1.0.parquet
```

## 6.1. Meaning of versions

### v0.x

Черновые версии:

```text
первичная очистка
проверка структуры
первые derived features
частичная валидация
```

### v1.0

Первая стабильная аналитическая версия:

```text
готова для основных моделей
зафиксированы критерии включения
зафиксирован словарь переменных
зафиксированы ключевые derived features
```

### v1.x

Минорные обновления:

```text
исправлены ошибки
добавлены derived features
обновлены отдельные переменные
не меняется принципиальная структура выборки
```

### v2.0

Мажорное обновление:

```text
новые batch данные
новые критерии включения
существенно изменилось n
существенно изменилось p
существенно изменился словарь переменных
```

---

## 7. Processed dataset manifest

Основной файл:

```text
data/processed/manifest.csv
```

Рекомендуемые колонки:

```text
dataset_version
file_name
created_at
created_by
source_batches
source_files
n_rows
n_columns
n_subjects
n_chord_positive
n_chord_negative
n_excluded_subjects
n_excluded_variables
code_version
params_version
variable_dictionary_version
data_audit_report
change_summary
status
```

Пример строки:

```csv
dataset_version,file_name,created_at,created_by,source_batches,source_files,n_rows,n_columns,n_subjects,n_chord_positive,n_chord_negative,n_excluded_subjects,n_excluded_variables,code_version,params_version,variable_dictionary_version,data_audit_report,change_summary,status
v0.1,dataset_v0.1.parquet,2026-05-10,Ars,batch_2026-05-10,final_analysis_dataset.xlsx,,,,,,,,,,,,Initial processed dataset after first audit,draft
```

---

## 8. Dataset version registry

| Dataset version | Created at | Source batches | n rows | n subjects | p variables | Status | Main changes |
|---|---:|---|---:|---:|---:|---|---|
| v0.1 | TBD | batch_2026-05-10 | TBD | ≈200 | ≈240 | planned | Initial processed dataset after first audit. |
| v0.2 | TBD | TBD | TBD | TBD | TBD | planned | Updated after feature engineering and variable dictionary refinement. |
| v1.0 | TBD | TBD | TBD | TBD | TBD | planned | First stable analytical dataset for primary mechanistic models. |

Status values:

```text
planned
draft
validated
analysis-ready
superseded
archived
```

---

## 9. Change log between dataset versions

Каждое изменение между версиями должно быть описано.

## 9.1. Template

```text
Dataset change:
From version:
To version:
Date:
Reason:
Source batches:
Code/script:
Parameters:
Rows added:
Rows removed:
Variables added:
Variables removed:
Variables renamed:
Derived features added:
Corrections:
Impact on previous analyses:
Requires rerun:
Notes:
```

## 9.2. Change log table

| From | To | Date | Rows changed | Variables changed | Main reason | Requires rerun | Notes |
|---|---|---:|---:|---:|---|---|---|
| raw | v0.1 | TBD | TBD | TBD | Initial cleaning and validation | yes | To be filled after first data audit. |
| v0.1 | v0.2 | TBD | TBD | TBD | Feature engineering update | yes | Planned. |
| v0.2 | v1.0 | TBD | TBD | TBD | Stable analysis-ready dataset | yes | Planned. |

---

## 10. Inclusion and exclusion criteria

## 10.1. Subject-level inclusion

Potential inclusion criteria:

```text
participant has usable echocardiography data
participant has false chord status or chord phenotype assessment
participant has key demographic covariates
participant has sufficient mechanics / strain variables for planned analysis
```

Final criteria must be updated after data audit.

## 10.2. Subject-level exclusion

Potential exclusion criteria:

```text
duplicate participant record without resolution
missing false chord status
unusable echocardiography record
extreme impossible physiological values not correctable
missing all key outcome domains
personal/test row or non-participant row
```

Do not exclude subjects only because their data weaken a hypothesis.

## 10.3. Variable-level inclusion

Potential inclusion criteria:

```text
variable has clear meaning
variable has known unit
variable belongs to a defined domain
variable has acceptable missingness
variable is not a personal identifier
variable is not a duplicate of another variable unless intentionally retained
```

## 10.4. Variable-level exclusion

Potential exclusion criteria:

```text
personal identifier
unknown meaning
unknown unit
excessive missingness
constant or near-constant variable
technical artifact
duplicate variable
data leakage variable
post-hoc variable not available for intended analysis
```

---

## 11. Subject inclusion registry

This table must be filled after the first data audit.

| Dataset version | Total rows | Unique subjects | Included subjects | Excluded subjects | Main exclusion reasons |
|---|---:|---:|---:|---:|---|
| v0.1 | TBD | TBD | TBD | TBD | TBD |
| v0.2 | TBD | TBD | TBD | TBD | TBD |
| v1.0 | TBD | TBD | TBD | TBD | TBD |

---

## 12. Variable inclusion registry

This table must be filled after the first data audit.

| Dataset version | Total variables | Included variables | Excluded variables | Derived variables | Main exclusion reasons |
|---|---:|---:|---:|---:|---|
| v0.1 | TBD | TBD | TBD | TBD | TBD |
| v0.2 | TBD | TBD | TBD | TBD | TBD |
| v1.0 | TBD | TBD | TBD | TBD | TBD |

---

## 13. Variable domain registry

Variables should be assigned to domains.

Expected domains:

```text
id
demographics
anthropometry
chord_phenotype
lv_geometry
lv_function
mechanics_global
mechanics_regional
strain_rate
time_to_peak
ecg
sport_training
technical_acquisition
derived_local_signature
derived_spatial_gradient
derived_topology
quality_control
exclude
```

After data audit, the actual list should be synchronized with:

```text
docs/VARIABLE_DICTIONARY.md
```

---

## 14. Personal data handling

The dataset may contain biomedical and personal data.

Potential identifiers:

```text
ФИО
date of birth
phone
email
address
medical record number
study ID linked to identity
raw exam ID
```

Rules:

```text
personal identifiers must not be included in processed analytical outputs;
personal identifiers must not be printed in logs;
personal identifiers must not be indexed by AI tools;
personal identifiers must not be committed to Git;
processed datasets should use anonymous participant_id;
linkage tables, if needed, must be stored separately and protected.
```

The `.aiexclude` file should exclude raw data and personal identifiers from AI indexing.

---

## 15. Data quality flags

The processed dataset should eventually include quality flags.

Possible flags:

```text
qc_missing_key_covariates
qc_missing_chord_status
qc_missing_mechanics_domain
qc_missing_ecg_domain
qc_impossible_value_detected
qc_outlier_candidate
qc_duplicate_subject
qc_low_confidence_chord_classification
qc_low_confidence_strain_measurement
qc_excluded_from_primary_analysis
```

These flags are useful because exclusion should be transparent.

---

## 16. Traceability of analyses

Every analysis output must reference a dataset version.

For every report, table, figure, or model, record:

```text
dataset_version
dataset_file
created_at
script_name
script_version / git commit if available
params.yaml version
random_seed
n_used
variables_used
exclusions_applied
```

Recommended run manifest:

```text
outputs/diagnostics/run_manifest.json
```

Example:

```json
{
  "run_id": "primary_models_2026-05-10_001",
  "dataset_version": "v0.1",
  "dataset_file": "data/processed/dataset_v0.1.parquet",
  "script": "scripts/train_model.py",
  "params_file": "params.yaml",
  "random_seed": 42,
  "n_used": null,
  "outputs": [
    "outputs/tables/primary_mechanistic_models.xlsx",
    "outputs/figures/spatial_gradient_plot.png"
  ],
  "notes": "Initial placeholder manifest structure."
}
```

---

## 17. Relationship with DVC

DVC should be used when the pipeline becomes stable.

Potential DVC stages:

```text
validate_data
build_dataset
feature_engineering
primary_models
bootstrap
export_tables
export_figures
```

Each DVC stage should specify:

```text
deps
params
outs
metrics if relevant
```

The DVC pipeline should make it possible to answer:

```text
Which raw data and which code produced this dataset version?
```

---

## 18. Relationship with MLflow

MLflow is used for model and experiment tracking.

Each MLflow run should log:

```text
dataset_version
hypothesis_id
model_type
predictors
outcomes
covariates
parameters
metrics
artifacts
random_seed
```

Do not use MLflow as a substitute for data provenance. MLflow tracks model runs; this document tracks data origin and dataset versions.

---

## 19. Known current limitations

Current limitations before the first data audit:

```text
exact variable names are not yet confirmed in this document;
exact number of subjects is approximate;
exact number of variables is approximate;
batch structure is planned and may need adaptation;
processed dataset versions are not yet created;
inclusion/exclusion criteria are preliminary;
personal identifier structure must be audited.
```

These limitations must be updated after:

```text
Stage 1 — Data audit
```

---

## 20. Update protocol

When new data are added:

1. Create a new `data/raw/batch_YYYY-MM-DD/` folder.
2. Copy raw files into the batch folder.
3. Add `metadata.yaml`.
4. Update batch registry in this file.
5. Run data validation.
6. Update source files registry.
7. Create a new processed dataset version.
8. Update `data/processed/manifest.csv`.
9. Update dataset version registry.
10. Document changes between dataset versions.
11. Rerun affected analyses.
12. Update reports and outputs with the new dataset version.

---

## 21. Minimal checklist for every dataset version

Before a dataset version can be used in primary analysis, confirm:

```text
[ ] dataset version is named correctly
[ ] source batch is documented
[ ] source files are documented
[ ] n rows is recorded
[ ] n subjects is recorded
[ ] p variables is recorded
[ ] included/excluded subjects are documented
[ ] included/excluded variables are documented
[ ] personal identifiers are removed or protected
[ ] variable dictionary is synchronized
[ ] missingness summary is generated
[ ] data audit report exists
[ ] processed dataset is listed in manifest.csv
[ ] analysis outputs reference this dataset version
```

---

## 22. Short rule

No result should be interpreted without knowing:

```text
which data version produced it
which subjects were included
which variables were included
which transformations were applied
which exclusions were made
```

Data provenance is part of the scientific evidence.
