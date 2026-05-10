# ANALYSIS_PLAN.md

# План анализа данных проекта `false-lv-chords`

## 1. Назначение документа

Этот документ описывает текущий план анализа данных для диссертационного проекта по изучению ложных хорд левого желудочка.

Важно: это **не финальная версия анализа**. Документ должен дополняться по мере появления:

- новых данных;
- новых гипотез;
- результатов первичного data audit;
- уточнённого словаря переменных;
- новых derived features;
- результатов промежуточного моделирования;
- замечаний научного руководителя;
- требований статьи или диссертации.

Текущая версия задаёт базовый исследовательский контур:

```text
data audit
→ feature engineering
→ descriptive physiology
→ primary mechanistic models
→ PCA by domains
→ Elastic Net / sparse PLS / Bayesian shrinkage
→ bootstrap stability
→ sensitivity analyses
→ biological interpretation
```

Главная цель анализа — не просто найти статистические связи, а проверить, какой биологический смысл могут иметь ложные хорды левого желудочка:

```text
анатомический вариант
механическое ограничение
топологическая связь между сегментами
модификатор региональной механики
маркер геометрического / функционального / ЭКГ-фенотипа
нейтральная находка без устойчивого сигнала
```

---

## 2. Исходные данные

Планируемое расположение проекта:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res
```

Основной исходный аналитический файл:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res\data\final_analysis_dataset.xlsx
```

Ожидаемый масштаб:

```text
n ≈ 200 participants
p ≈ 240 variables
```

Рабочая структура данных в проекте:

```text
data/
├─ raw/          # исходные данные
├─ interim/      # промежуточные очищенные данные
├─ processed/    # финальные аналитические датасеты
└─ README.md
```

Основной принцип:

```text
data/raw/ не изменяется вручную
```

Все преобразования должны быть воспроизводимыми через код.

---

## 3. Общие аналитические принципы

### 3.1. Не начинать с массовых корреляций

Запрещённый подход:

```text
240 variables → all pairwise correlations → p < 0.05 → interpretation
```

Правильная логика:

```text
scientific hypothesis
→ variable roles
→ domain structure
→ feature engineering
→ adjusted models
→ stability
→ sensitivity
→ physiological interpretation
```

### 3.2. EF не является главным исходом

Фракция выброса может быть сохранной даже при наличии региональных механических различий.

Основной фокус:

```text
regional mechanics
strain
strain rate
time to peak strain
mechanical dispersion
insertion / adjacent / remote contrasts
spatial gradient
topological features
```

### 3.3. Разделять предикторы, исходы, ковариаты и медиаторы

Каждая переменная должна быть отнесена к одной или нескольким ролям:

```text
id variable
chord predictor
baseline covariate
possible confounder
possible mediator
mechanics outcome
geometry outcome
function outcome
ECG outcome
derived feature
technical / acquisition variable
```

Важно:

Если предполагается путь:

```text
false chord → LV geometry → strain → EF / ECG
```

то геометрия может быть медиатором, а не простой ковариатой.

### 3.4. Устойчивость важнее единичного p-value

Результат должен оцениваться по совокупности критериев:

```text
effect size
direction
confidence interval / credible interval
bootstrap stability
selection frequency
FDR correction
sensitivity analysis
physiological plausibility
```

---

## 4. Версионность плана анализа

Поскольку план будет дополняться, все новые гипотезы и изменения должны фиксироваться в этом документе или в связанных файлах.

Рекомендуемый формат добавления новой гипотезы:

```text
Hypothesis ID:
Date added:
Scientific question:
Variables needed:
Predictors:
Outcomes:
Covariates:
Derived features:
Primary model:
Robustness checks:
Expected outputs:
Interpretation rules:
Status:
```

Пример:

```text
Hypothesis ID: H_REGIONAL_001
Date added: 2026-05-10
Scientific question: Are insertion segments mechanically different from remote segments?
Predictors: insertion / adjacent / remote zone type
Outcomes: segmental strain, strain rate, time-to-peak strain
Covariates: age, sex, BSA
Derived features: insertion_minus_remote_strain
Primary model: adjusted linear model or mixed segment-level model
Robustness checks: bootstrap, outlier exclusion, alternative covariates
Expected outputs: regional contrast table, gradient plot
Interpretation rules: local effect supports mechanical constraint hypothesis
Status: planned
```

---

## 5. Stage 1 — Data audit

## 5.1. Цель

Проверить, можно ли использовать датасет для воспроизводимого научного анализа.

Data audit должен ответить на вопросы:

```text
Сколько наблюдений реально доступно?
Сколько переменных реально доступно?
Есть ли дубликаты?
Есть ли персональные идентификаторы?
Какие переменные имеют много пропусков?
Какие переменные имеют невозможные значения?
Какие переменные являются числовыми, категориальными, бинарными?
Есть ли признаки неправильных единиц измерения?
Есть ли переменные, которые нельзя использовать без очистки?
```

## 5.2. Входы

```text
data/final_analysis_dataset.xlsx
data/raw/*
docs/VARIABLE_DICTIONARY.md, если уже создан
params.yaml, если уже создан
```

## 5.3. Основные проверки

### Структура датасета

```text
number of rows
number of columns
column names
duplicated columns
duplicated rows
duplicated participant IDs
```

### Типы переменных

```text
numeric
categorical
binary
date
text
identifier
unknown
```

### Пропуски

```text
missingness per variable
missingness per participant
missingness by domain
missingness pattern
variables with high missingness
```

### Невозможные значения

Примеры:

```text
negative age
impossible height
impossible weight
EF outside physiological range
invalid ECG intervals
invalid strain values
impossible dates
```

### Выбросы

```text
univariate outliers
domain-specific outliers
physiologically impossible outliers
technically suspicious outliers
```

### Персональные данные

Нужно проверить наличие:

```text
ФИО
даты рождения
телефоны
email
адреса
номера документов
медицинские идентификаторы
```

Такие переменные не должны попадать в публичные outputs.

## 5.4. Ожидаемые outputs

```text
outputs/diagnostics/data_audit_report.md
outputs/tables/variable_type_audit.xlsx
outputs/tables/missingness_summary.xlsx
outputs/tables/descriptive_statistics_raw.xlsx
outputs/tables/outlier_candidates.xlsx
outputs/figures/missingness_heatmap.png
outputs/figures/domain_missingness_plot.png
outputs/diagnostics/data_audit_manifest.json
```

## 5.5. Критерии перехода к следующему этапу

Переход к feature engineering возможен, если:

```text
определены основные типы переменных
понятны критические пропуски
нет необработанных персональных идентификаторов в аналитическом наборе
создан список переменных для исключения
создан список переменных для ручной проверки
создана первая версия словаря переменных
```

---

## 6. Stage 2 — Feature engineering

## 6.1. Цель

Создать физиологически осмысленные признаки, которые позволяют проверить механистические гипотезы.

Feature engineering должен быть основан на научной рамке проекта, а не на слепом переборе переменных.

Главные группы derived features:

```text
chord phenotype features
domain-level features
regional mechanics features
insertion / adjacent / remote features
spatial gradient features
topological features
mechanical heterogeneity features
```

## 6.2. Chord phenotype features

Признаки, описывающие саму хорду:

```text
false_chord_presence
false_chord_count
false_chord_location
false_chord_orientation
false_chord_attachment_1
false_chord_attachment_2
false_chord_segment_from
false_chord_segment_to
false_chord_basal_mid_apical_class
false_chord_septal_freewall_class
false_chord_topological_class
```

Фактические имена переменных должны быть взяты из датасета и `VARIABLE_DICTIONARY.md`.

## 6.3. Local mechanical signature features

Основная идея:

```text
insertion segments vs adjacent segments vs remote segments
```

Возможные признаки:

```text
insertion_mean_strain
adjacent_mean_strain
remote_mean_strain

insertion_mean_strain_rate
adjacent_mean_strain_rate
remote_mean_strain_rate

insertion_mean_time_to_peak
adjacent_mean_time_to_peak
remote_mean_time_to_peak

insertion_minus_adjacent_strain
insertion_minus_remote_strain
adjacent_minus_remote_strain

insertion_minus_adjacent_time_to_peak
insertion_minus_remote_time_to_peak
```

## 6.4. Spatial gradient features

Признаки, отражающие изменение механики по мере удаления от хорды:

```text
strain_gradient_slope
strain_rate_gradient_slope
time_to_peak_gradient_slope
gradient_magnitude
gradient_direction
gradient_stability
```

Пример логики:

```text
distance 0 = insertion
distance 1 = adjacent
distance 2 = remote
```

## 6.5. Topological features

ЛЖ представляется как граф сегментов.

```text
segments = nodes
anatomical adjacency = edges
false chord = additional internal edge
```

Возможные признаки:

```text
chord_node_1
chord_node_2
chord_edge
chord_edge_class
is_chord_connected_segment
is_adjacent_to_chord_segment
is_remote_segment
graph_distance_to_chord
mean_strain_chord_connected_nodes
mean_strain_remote_nodes
connected_vs_remote_difference
mechanical_coupling_connected_segments
```

## 6.6. Domain-level features

Признаки по доменам:

```text
mechanics_domain_score
geometry_domain_score
function_domain_score
ecg_domain_score
mechanical_heterogeneity_index
global_regional_discordance_index
```

Их точное определение должно появиться после data audit и анализа структуры переменных.

## 6.7. Ожидаемые outputs

```text
data/interim/features_intermediate.parquet
data/processed/dataset_v0.1.parquet
outputs/tables/feature_dictionary.xlsx
outputs/tables/derived_features_summary.xlsx
outputs/diagnostics/feature_engineering_report.md
outputs/diagnostics/feature_engineering_manifest.json
```

---

## 7. Stage 3 — Descriptive physiology

## 7.1. Цель

Описать физиологическую структуру выборки до моделирования.

Этот этап должен показать:

```text
кто входит в выборку
какие типы хорд представлены
как распределены домены механики, геометрии, функции и ЭКГ
есть ли очевидные физиологические паттерны
какие переменные требуют трансформации или осторожной интерпретации
```

## 7.2. Основные описательные блоки

### Участники

```text
age
sex
height
weight
BSA
sport / training group if available
diagnosis / group if available
```

### Хорды

```text
presence
count
location
orientation
attachment pattern
topological class
single vs multiple
```

### Геометрия ЛЖ

```text
LV volumes
LV dimensions
LV mass if available
relative geometry indices if available
```

### Функция

```text
EF
stroke volume if available
diastolic indices if available
```

### Механика

```text
GLS
segmental strain
strain rate
time to peak strain
mechanical dispersion
regional heterogeneity
```

### ЭКГ

```text
heart rate
PR
QRS
QT
QTc
axis or conduction markers if available
repolarization markers if available
```

## 7.3. Ожидаемые outputs

```text
outputs/tables/descriptive_physiology.xlsx
outputs/tables/chord_phenotype_distribution.xlsx
outputs/tables/domain_summary_statistics.xlsx
outputs/figures/chord_distribution_plot.png
outputs/figures/mechanics_distribution_plot.png
outputs/figures/geometry_distribution_plot.png
outputs/figures/ecg_distribution_plot.png
outputs/reports/descriptive_physiology_report.md
```

## 7.4. Интерпретация

Descriptive physiology не должна превращаться в набор случайных таблиц.

Каждый вывод должен быть связан с вопросом:

```text
Что это говорит о возможном биологическом смысле ложных хорд?
```

---

## 8. Stage 4 — Primary mechanistic models

## 8.1. Цель

Проверить первичные механистические гипотезы.

Главный вопрос:

```text
Связан ли фенотип ложной хорды с региональной механикой, геометрией, функцией или ЭКГ после учёта ключевых ковариат?
```

## 8.2. Базовая логика вложенных моделей

Для каждого основного исхода сравниваются две модели.

### Base model

```text
outcome ~ age + sex + BSA + justified covariates
```

### Chord model

```text
outcome ~ age + sex + BSA + justified covariates + chord phenotype
```

Основной интерес:

```text
Does chord phenotype add explanatory signal beyond baseline covariates?
```

## 8.3. Первичные исходы

Приоритетные исходы:

```text
local/regional strain contrasts
spatial gradient features
mechanical dispersion
domain-level mechanics scores
geometry domain scores
ECG domain scores
EF only as secondary global outcome
```

## 8.4. Primary mechanistic hypotheses

### H_MECH_001 — Local mechanical signature

```text
Insertion segments differ from remote segments in regional mechanics.
```

Possible outcomes:

```text
insertion_minus_remote_strain
insertion_minus_remote_strain_rate
insertion_minus_remote_time_to_peak
```

### H_MECH_002 — Spatial gradient

```text
Mechanical difference decreases with distance from chord insertion.
```

Possible outcomes:

```text
strain_gradient_slope
time_to_peak_gradient_slope
```

### H_MECH_003 — Phenotype-specific effect

```text
Different chord orientations or locations have different mechanical signatures.
```

Possible predictors:

```text
chord_orientation
chord_location
chord_topological_class
```

### H_GEOM_001 — Geometry phenotype

```text
False chord phenotype is associated with LV geometry domain features.
```

### H_FUNC_001 — Global function

```text
False chord phenotype is weakly or not associated with EF after covariate adjustment.
```

This hypothesis is important because a null EF result may support the idea that the effect is regional rather than global.

### H_ECG_001 — ECG association

```text
False chord phenotype is associated with ECG features only if the effect is stable and physiologically interpretable.
```

## 8.5. Possible model families

Initial models:

```text
linear regression
robust linear regression
generalized linear models if needed
mixed-effects models for segment-level data
permutation-based model comparison
```

Use mixed models if data are reshaped to segment-level long format:

```text
segmental_strain ~ zone_type + chord_phenotype + covariates + (1 | participant_id)
```

## 8.6. Expected outputs

```text
outputs/tables/primary_mechanistic_models.xlsx
outputs/tables/model_comparison_base_vs_chord.xlsx
outputs/tables/regional_contrast_models.xlsx
outputs/tables/spatial_gradient_models.xlsx
outputs/figures/primary_effect_size_plot.png
outputs/figures/spatial_gradient_plot.png
outputs/figures/insertion_adjacent_remote_plot.png
outputs/reports/primary_mechanistic_models_report.md
```

---

## 9. Stage 5 — PCA by domains

## 9.1. Цель

Снизить размерность внутри физиологически осмысленных доменов и получить интерпретируемые latent axes.

PCA должна проводиться отдельно по доменам:

```text
mechanics
regional strain
geometry
function
ECG
possibly chord phenotype if variables allow
```

Не следует выполнять одну общую PCA по всем переменным без физиологического смысла.

## 9.2. Основные шаги

```text
select domain variables
exclude variables with excessive missingness
impute or handle missing values according to predefined rule
scale variables
run PCA
save explained variance
save loadings
interpret components physiologically
create domain scores
```

## 9.3. Возможные интерпретации компонент

```text
PC1_mechanics = global deformation axis
PC2_mechanics = regional heterogeneity axis
PC1_geometry = LV size/remodeling axis
PC2_geometry = shape/proportionality axis
PC1_ECG = conduction/repolarization axis
```

Интерпретация должна основываться на loadings, а не на названии компоненты заранее.

## 9.4. Использование PCA scores

PCA scores могут использоваться как исходы:

```text
PC1_mechanics ~ covariates + chord phenotype
PC2_mechanics ~ covariates + chord phenotype
PC1_geometry ~ covariates + chord phenotype
PC1_ECG ~ covariates + chord phenotype
```

## 9.5. Expected outputs

```text
outputs/tables/pca_explained_variance.xlsx
outputs/tables/pca_loadings_by_domain.xlsx
outputs/tables/pca_scores_summary.xlsx
outputs/figures/pca_explained_variance_mechanics.png
outputs/figures/pca_loadings_mechanics.png
outputs/figures/pca_scores_by_chord_phenotype.png
outputs/reports/pca_domain_report.md
```

---

## 10. Stage 6 — Elastic Net / sparse PLS / Bayesian shrinkage

## 10.1. Цель

Использовать дополнительные модели не как замену физиологической логике, а как слой устойчивого поиска многомерных закономерностей.

Эти методы отвечают на разные вопросы:

```text
Elastic Net:
Какие признаки стабильно выбираются среди коррелированных переменных?

Sparse PLS:
Какой паттерн chord phenotype связан с паттерном cardiac phenotype?

Bayesian shrinkage:
Насколько устойчив и вероятен эффект у выбранных кандидатных гипотез?
```

---

## 10.2. Elastic Net

### Назначение

Elastic Net используется для:

```text
feature selection stability
incremental predictive value
handling correlated predictors
ranking candidate chord features
```

### Базовая логика

Сравнить:

```text
Base model:
outcome ~ covariates

Extended model:
outcome ~ covariates + chord features + derived features
```

### Возможные outcomes

```text
PC1_mechanics
PC2_mechanics
insertion_minus_remote_strain
strain_gradient_slope
PC1_geometry
PC1_ECG
```

### Outputs

```text
outputs/tables/elastic_net_model_results.xlsx
outputs/tables/elastic_net_selection_frequency.xlsx
outputs/tables/elastic_net_coefficient_stability.xlsx
outputs/figures/elastic_net_selection_frequency.png
```

---

## 10.3. Sparse PLS

### Назначение

Sparse PLS используется для поиска связи между блоками:

```text
X = chord phenotype / topology features
Y = mechanics / geometry / ECG features
```

### Интерпретация

Sparse PLS не доказывает причинность.

Корректная формулировка:

```text
A chord phenotype pattern characterized by [features] was associated with a cardiac phenotype pattern characterized by [features].
```

### Outputs

```text
outputs/tables/sparse_pls_x_loadings.xlsx
outputs/tables/sparse_pls_y_loadings.xlsx
outputs/tables/sparse_pls_scores.xlsx
outputs/figures/sparse_pls_biplot.png
outputs/reports/sparse_pls_report.md
```

---

## 10.4. Bayesian shrinkage

### Назначение

Bayesian shrinkage используется для 1–3 наиболее интересных кандидатных гипотез после первичного анализа.

Не использовать Bayesian modeling как декоративный метод.

### Возможные модели

```text
Bayesian linear regression
Bayesian hierarchical model
Bayesian shrinkage priors
```

### Outputs

```text
outputs/tables/bayesian_candidate_models.xlsx
outputs/figures/bayesian_posterior_intervals.png
outputs/reports/bayesian_interpretation_report.md
```

### Что сообщать

```text
posterior mean
95% credible interval
posterior probability of direction
practical significance
```

---

## 11. Stage 7 — Bootstrap stability

## 11.1. Цель

Проверить, насколько результаты устойчивы к изменению выборки.

Bootstrap должен использоваться для:

```text
effect stability
direction stability
feature selection stability
confidence interval estimation
model comparison stability
```

## 11.2. Основные показатели

```text
bootstrap_mean_effect
bootstrap_median_effect
bootstrap_confidence_interval
sign_stability
selection_frequency
proportion_of_models_with_same_direction
```

## 11.3. Интерпретация стабильности

Примерная шкала:

```text
selection frequency > 0.80
    strong stability

selection frequency 0.60–0.80
    moderate stability

selection frequency 0.40–0.60
    weak / uncertain stability

selection frequency < 0.40
    unstable
```

Эта шкала является рабочей и может быть уточнена.

## 11.4. Outputs

```text
outputs/tables/bootstrap_effect_stability.xlsx
outputs/tables/bootstrap_selection_frequency.xlsx
outputs/figures/bootstrap_effect_intervals.png
outputs/figures/bootstrap_selection_frequency.png
outputs/reports/bootstrap_stability_report.md
```

---

## 12. Stage 8 — Sensitivity analyses

## 12.1. Цель

Проверить, не является ли результат артефактом конкретного решения анализа.

Sensitivity analyses должны оценивать:

```text
alternative covariate sets
outlier exclusion
missing data strategy
sex-specific models
age-adjusted models
sport/training group adjustment if available
different chord phenotype encodings
different definitions of adjacent/remote segments
different PCA component counts
different FDR families
```

## 12.2. Основные sensitivity checks

### Alternative covariate sets

```text
Model A: age + sex + BSA
Model B: age + sex + BSA + heart rate
Model C: age + sex + BSA + sport/training group
Model D: age + sex + height + weight instead of BSA
```

### Outlier sensitivity

```text
full sample
excluding extreme physiological outliers
excluding high-influence observations
robust regression
```

### Missing data sensitivity

```text
complete case
simple imputation
domain-specific imputation
missingness indicator if justified
```

### Chord encoding sensitivity

```text
presence only
presence + count
phenotype classes
topological classes
insertion-based features
```

### Regional definition sensitivity

```text
strict insertion only
insertion + immediate adjacent
graph-distance-based zones
alternative remote definition
```

## 12.3. Outputs

```text
outputs/tables/sensitivity_analysis_summary.xlsx
outputs/tables/covariate_set_comparison.xlsx
outputs/tables/outlier_sensitivity_results.xlsx
outputs/tables/missing_data_sensitivity_results.xlsx
outputs/figures/sensitivity_effect_comparison.png
outputs/reports/sensitivity_analysis_report.md
```

---

## 13. Final integration — Biological interpretation

After all analytical stages, results should be integrated into a biological conclusion.

The conclusion must classify the evidence into one of several scenarios.

### Scenario A — Neutral anatomical variant

```text
No stable associations with mechanics, geometry, function, ECG, or topology.
```

Interpretation:

```text
In this dataset, false chords behave as an anatomical variant without detectable biological signal.
```

### Scenario B — Global phenotype marker

```text
Associations exist with global geometry/function/ECG but not with regional mechanics.
```

Interpretation:

```text
False chords may be markers of a broader structural phenotype rather than local mechanical constraints.
```

### Scenario C — Local mechanical modifier

```text
Stable insertion vs remote differences are present.
```

Interpretation:

```text
False chords may act as local modifiers of myocardial mechanics.
```

### Scenario D — Spatial gradient pattern

```text
Effect decreases from insertion to adjacent to remote segments.
```

Interpretation:

```text
This supports the internal mechanical constraint hypothesis.
```

### Scenario E — Topological phenotype

```text
Graph-based chord features explain regional mechanics better than binary chord presence.
```

Interpretation:

```text
False chords may function as topological links between LV segments.
```

### Scenario F — Multidomain phenotype

```text
Chord phenotype is linked to coordinated mechanics, geometry, and ECG patterns.
```

Interpretation:

```text
False chords may represent part of a broader cardiac structural-mechanical-electrical phenotype.
```

---

## 14. Current planned outputs

At the current stage, the project should aim to generate:

```text
outputs/reports/data_audit_report.md
outputs/reports/descriptive_physiology_report.md
outputs/reports/primary_mechanistic_models_report.md
outputs/reports/pca_domain_report.md
outputs/reports/bootstrap_stability_report.md
outputs/reports/sensitivity_analysis_report.md

outputs/tables/descriptive_statistics.xlsx
outputs/tables/chord_phenotype_distribution.xlsx
outputs/tables/feature_dictionary.xlsx
outputs/tables/primary_mechanistic_models.xlsx
outputs/tables/pca_loadings_by_domain.xlsx
outputs/tables/elastic_net_selection_frequency.xlsx
outputs/tables/bootstrap_effect_stability.xlsx
outputs/tables/sensitivity_analysis_summary.xlsx

outputs/figures/missingness_heatmap.png
outputs/figures/domain_correlation_heatmap.png
outputs/figures/insertion_adjacent_remote_plot.png
outputs/figures/spatial_gradient_plot.png
outputs/figures/pca_explained_variance.png
outputs/figures/elastic_net_selection_frequency.png
outputs/figures/bootstrap_effect_intervals.png
```

---

## 15. Relationship with other project documents

This file should be read together with:

```text
docs/SCIENTIFIC_FRAMEWORK.md
```

Defines the physiological and mechanistic theory.

```text
docs/STATISTICAL_GUARDRAILS.md
```

Defines statistical restrictions, multiple testing strategy, robustness requirements, and anti-p-hacking rules.

```text
docs/VARIABLE_DICTIONARY.md
```

Defines actual variables, domains, units, roles, and allowed transformations.

```text
docs/DATA_PROVENANCE.md
```

Defines origin, versioning, and traceability of data.

```text
docs/PUBLICATION_STRATEGY.md
```

Defines how analytical results should be converted into dissertation/manuscript narrative.

---

## 16. Current status

Current status:

```text
planned / living document
```

The plan is ready to guide the first implementation of:

```text
data audit
feature engineering
descriptive physiology
primary mechanistic models
```

The plan must be updated after the first real data audit because actual variable names, missingness, distributions, and domain completeness may change the feasible modeling strategy.
