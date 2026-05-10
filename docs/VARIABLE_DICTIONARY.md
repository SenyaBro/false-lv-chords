# VARIABLE_DICTIONARY.md

# Словарь переменных проекта `false-lv-chords`

## 1. Назначение документа

Этот документ является canonical-словарём переменных для проекта по изучению ложных хорд левого желудочка.

Его задача — зафиксировать для каждой переменной:

```text
название переменной
исходное/русское название
домен
тип
единицы измерения
биологический смысл
роль в модели
допустимые значения
missing codes
статус включения
аналоги/старые названия
```

Этот файл должен дополняться после каждого этапа:

```text
data audit
feature engineering
обновление dataset version
добавление нового batch
изменение правил анализа
```

---

## 2. Что делать со старым Excel-словарём

Старый словарь `dictional_filled_column_name.xlsx` нужно сохранить, но не использовать как единственный рабочий источник.

Рекомендуемая схема:

```text
references/notes/legacy_variable_dictionary/dictional_filled_column_name.xlsx
```

или:

```text
docs/_archive/legacy_variable_dictionary_2026-05-10.xlsx
```

Лучший вариант для проекта:

```text
references/notes/legacy_variable_dictionary/dictional_filled_column_name.xlsx
```

Почему так:

- это не сырые пациентские данные;
- это полезный исторический источник названий и аналогов;
- Excel-файл не должен быть главным живым словарём;
- AI-агенты обычно не должны индексировать `.xlsx`;
- canonical-версия должна быть в `docs/VARIABLE_DICTIONARY.md`;
- позже можно дополнительно сделать машинно-читаемую версию `config/variables.yml`.

Итоговая логика:

```text
legacy Excel dictionary
→ migrated canonical Markdown dictionary
→ later config/variables.yml for code
```

---

## 3. Источник первичной миграции

Первичная версия этого документа основана на старом Excel-словаре:

```text
dictional_filled_column_name.xlsx
```

В старом словаре обнаружены колонки:

```text
Russian_Meaning
Block
Column_Name
Analogue
```

Количество переменных в старом словаре:

```text
204
```

Распределение по legacy-блокам:

| Legacy block | New proposed domain | Variables |
|---|---|---:|
| Chords | chord_phenotype | 33 |
| Electr | ecg | 8 |
| F | lv_function_echo | 13 |
| GM | lv_geometry | 32 |
| General | demographics_anthropometry | 8 |
| Reg_Mech | regional_mechanics_dicor | 32 |
| Strein | regional_strain_ste | 54 |
| Strein_CHORDS | chord_attachment_topology | 18 |
| Work | exercise_test | 6 |

---

## 4. Canonical schema для переменной

Каждая переменная должна описываться по следующей схеме.

| Поле | Смысл |
|---|---|
| `variable_name` | Каноническое английское имя переменной в датасете |
| `source_name_ru` | Русское или исходное название переменной |
| `legacy_block` | Старый блок из Excel-словаря |
| `domain` | Новый аналитический домен |
| `subdomain` | Более точный поддомен, если нужен |
| `data_type` | numeric, integer, binary, categorical, text, date, identifier |
| `unit` | Единица измерения |
| `biological_meaning` | Что переменная означает физиологически |
| `model_role` | predictor, outcome, covariate, mediator, technical, exclude |
| `allowed_values` | Допустимые значения или диапазон |
| `missing_codes` | Какие значения означают пропуск |
| `quality_rules` | Проверки качества |
| `transformation` | Масштабирование, логика расчёта, z-score и т.д. |
| `inclusion_status` | include, exclude, derived, pending, audit_required |
| `analogue` | Старое/альтернативное название |
| `notes` | Комментарии |

---

## 5. Домены переменных

Рекомендуемые домены проекта:

| Domain | Meaning |
|---|---|
| `demographics_anthropometry` | Возраст, пол, рост, вес, BSA, ИМТ, группы |
| `chord_phenotype` | Признаки ложных хорд ЛЖ |
| `chord_attachment_topology` | Привязка хорд к STE-сегментам и топологические признаки |
| `lv_geometry` | Геометрия и морфометрия ЛЖ |
| `lv_function_echo` | Стандартные ЭхоКГ-функциональные показатели |
| `regional_mechanics_dicor` | Региональная механика / DICOR-показатели |
| `regional_strain_ste` | Segmental strain, strain rate, time-to-peak strain |
| `ecg` | Электрокардиографические параметры |
| `exercise_test` | Нагрузочные/восстановительные показатели |
| `derived_local_signature` | Insertion / adjacent / remote derived features |
| `derived_spatial_gradient` | Признаки spatial gradient |
| `derived_topology` | Графовые/топологические признаки |
| `technical_acquisition` | Технические параметры измерений |
| `quality_control` | QC-флаги |
| `exclude` | Идентификаторы, персональные данные, служебные поля |

---

## 6. Роли переменных в моделях

| Model role | Meaning |
|---|---|
| `primary_predictor` | Основной предиктор: фенотип ложной хорды |
| `derived_topological_predictor` | Производный топологический/локальный предиктор |
| `baseline_covariate` | Базовая ковариата: возраст, пол, BSA и т.д. |
| `covariate_or_grouping` | Ковариата или группирующий фактор |
| `mechanics_outcome` | Исход механики |
| `regional_mechanics_outcome` | Региональный STE/mechanics исход |
| `geometry_outcome_or_mediator` | Геометрический исход или возможный медиатор |
| `secondary_function_outcome` | Функциональный исход, EF и др. |
| `ecg_outcome` | ЭКГ-исход |
| `exercise_covariate_or_secondary_outcome` | Нагрузочный показатель |
| `technical_variable` | Техническая переменная |
| `quality_control` | QC-флаг |
| `exclude_identifier` | Исключить из анализа и outputs |

---

## 7. Missing codes

До data audit нельзя жёстко утверждать, какие значения являются пропусками.

Потенциальные missing codes:

```text
empty cell
NA
N/A
NaN
None
null
.
-
999
-999
```

Важно:

```text
0 не является missing code автоматически.
```

Особенно для:

```text
count variables
flag variables
absence/presence variables
```

Например:

```text
lv_false_tendon_total_count = 0
```

может означать реальное отсутствие ложных хорд, а не пропуск.

---

## 8. Правила именования новых переменных

Новые derived features должны использовать snake_case.

Примеры:

```text
insertion_mean_strain_pct
adjacent_mean_strain_pct
remote_mean_strain_pct
insertion_minus_remote_strain_pct
strain_gradient_slope
time_to_peak_gradient_slope
graph_distance_to_chord
is_chord_connected_segment
mechanical_coupling_connected_segments
```

Правила:

- не использовать пробелы;
- не использовать кириллицу в именах переменных;
- единицу измерения желательно включать в имя, если это не ухудшает читаемость;
- derived features должны иметь понятный источник;
- переменная должна быть описана в этом файле перед использованием в confirmatory analysis.

---

## 9. Initial migrated dictionary from legacy Excel

Статус этой таблицы:

```text
draft_migrated_from_legacy_excel
```

Ограничения:

- типы и единицы частично выведены автоматически из названий переменных;
- допустимые диапазоны нужно уточнить после data audit;
- missing codes нужно проверить на реальных данных;
- biological meaning для части переменных является первичным описанием и требует экспертной правки;
- model_role может измениться после уточнения DAG и analysis plan.

| variable_name | source_name_ru | legacy_block | domain | data_type | unit | model_role | allowed_values | missing_codes | biological_meaning | analogue |
|---|---|---|---|---|---|---|---|---|---|---|
| `subject_full_name` | ФИО | General | demographics_anthropometry | identifier/text | TBD | exclude_identifier | text; exclude from analysis outputs | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: ФИО | name |
| `special_health_needs_flag` | ОВЗ | General | demographics_anthropometry | binary | 0/1 | covariate_or_grouping | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: ОВЗ | OVS |
| `age_years` | возраст | General | demographics_anthropometry | numeric_continuous | years | baseline_covariate | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: возраст | age |
| `height_cm` | рост | General | demographics_anthropometry | numeric_continuous | cm | baseline_covariate | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: рост | height |
| `weight_kg` | вес | General | demographics_anthropometry | numeric_continuous | kg | baseline_covariate | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: вес | weight |
| `body_surface_area_m2` | BSA | General | demographics_anthropometry | numeric_continuous | m² | baseline_covariate | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: BSA |  |
| `sex` | пол | General | demographics_anthropometry | categorical | category | baseline_covariate | TBD after audit; do not assume coding | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: пол | sex |
| `body_mass_index_kg_m2` | ИМТ | General | demographics_anthropometry | numeric_continuous | kg/m² | baseline_covariate | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Baseline participant characteristic: ИМТ | IMT |
| `echo_ascending_aorta_diameter_mm` | Ао восходящая | F | lv_function_echo | numeric_continuous | mm | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: Ао восходящая | Восходящая Ао |
| `echo_aortic_sinus_diameter_mm` | Ао синус | F | lv_function_echo | numeric_continuous | mm | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: Ао синус | Диаметр корня Ао |
| `echo_aortic_valve_annulus_diameter_mm` | Ао ФК | F | lv_function_echo | numeric_continuous | mm | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: Ао ФК |  |
| `echo_aortic_cusp_separation_mm` | ACS | F | lv_function_echo | numeric_continuous | mm | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: ACS |  |
| `echo_mitral_e_to_a_ratio` | Е/А | F | lv_function_echo | numeric_continuous | ratio | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: Е/А | Е//А |
| `echo_lv_end_diastolic_volume_teichholz_ml` | КДО Тейх | F | lv_function_echo | numeric_continuous | ml | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: КДО Тейх | КДО УЗИ |
| `echo_lv_end_systolic_volume_teichholz_ml` | КСО Тейх | F | lv_function_echo | numeric_continuous | ml | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: КСО Тейх | КСО УЗИ |
| `echo_lv_ejection_fraction_teichholz_pct` | ФВ Тейх | F | lv_function_echo | numeric_continuous | % | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: ФВ Тейх | ФИ УЗИ |
| `echo_lv_stroke_volume_teichholz_ml` | УО Тейх | F | lv_function_echo | numeric_continuous | ml | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: УО Тейх | УО |
| `echo_lv_end_diastolic_volume_simpson_ml` | КДО Симп | F | lv_function_echo | numeric_continuous | ml | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: КДО Симп | edv |
| `echo_lv_end_systolic_volume_simpson_ml` | КСО Симп | F | lv_function_echo | numeric_continuous | ml | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: КСО Симп | esv |
| `echo_lv_ejection_fraction_simpson_pct` | ФВ Симп | F | lv_function_echo | numeric_continuous | % | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: ФВ Симп | ef |
| `echo_lv_stroke_volume_simpson_ml` | УО Симп | F | lv_function_echo | numeric_continuous | ml | secondary_function_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Standard echocardiographic functional variable: УО Симп |  |
| `echo_lv_end_diastolic_diameter_mm` | КДР | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: КДР |  |
| `echo_lv_end_systolic_diameter_mm` | КСР | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: КСР |  |
| `echo_lv_myocardial_mass_index_g_m2` | ИММ | GM | lv_geometry | numeric_continuous | m² | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: ИММ |  |
| `echo_lv_relative_wall_thickness_ratio` | ОТС | GM | lv_geometry | numeric_continuous | ratio | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: ОТС | ОТС УЗИ |
| `echo_interventricular_septum_thickness_mm` | МЖП | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МЖП | МЖП УЗИ |
| `echo_lv_posterior_wall_thickness_mm` | ЗС | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: ЗС | ЗС ЛЖ УЗИ |
| `echo_lv_sphericity_index_end_systolic_ratio` | ИС КС | GM | lv_geometry | numeric_continuous | ratio | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: ИС КС |  |
| `echo_lv_sphericity_index_end_diastolic_ratio` | ИС КД | GM | lv_geometry | numeric_continuous | ratio | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: ИС КД |  |
| `dicor_mk_kdtr_01_mm` | МК КДТР 1 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК КДТР 1 |  |
| `dicor_mk_ous_01_pct` | МК ОУС 1 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК ОУС 1 |  |
| `dicor_mk_kdtr_02_mm` | МК КДТР 2 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК КДТР 2 |  |
| `dicor_mk_ous_02_pct` | МК ОУС 2 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК ОУС 2 |  |
| `dicor_mk_kdtr_03_mm` | МК КДТР 3 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК КДТР 3 |  |
| `dicor_mk_ous_03_pct` | МК ОУС 3 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК ОУС 3 |  |
| `dicor_mk_kdtr_04_mm` | МК КДТР 4 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК КДТР 4 |  |
| `dicor_mk_ous_04_pct` | МК ОУС 4 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: МК ОУС 4 |  |
| `dicor_sm_kdtr_01_mm` | СМ КДТР 1 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ КДТР 1 |  |
| `dicor_sm_ous_01_pct` | СМ ОУС 1 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ ОУС 1 |  |
| `dicor_sm_kdtr_02_mm` | СМ КДТР 2 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ КДТР 2 |  |
| `dicor_sm_ous_02_pct` | СМ ОУС 2 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ ОУС 2 |  |
| `dicor_sm_kdtr_03_mm` | СМ КДТР 3 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ КДТР 3 |  |
| `dicor_sm_ous_03_pct` | СМ ОУС 3 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ ОУС 3 |  |
| `dicor_sm_kdtr_04_mm` | СМ КДТР 4 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ КДТР 4 |  |
| `dicor_sm_ous_04_pct` | СМ ОУС 4 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: СМ ОУС 4 |  |
| `dicor_v_kdtr_01_mm` | В КДТР 1 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В КДТР 1 |  |
| `dicor_v_ous_01_pct` | В ОУС 1 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В ОУС 1 |  |
| `dicor_v_kdtr_02_mm` | В КДТР 2 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В КДТР 2 |  |
| `dicor_v_ous_02_pct` | В ОУС 2 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В ОУС 2 |  |
| `dicor_v_kdtr_03_mm` | В КДТР 3 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В КДТР 3 |  |
| `dicor_v_ous_03_pct` | В ОУС 3 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В ОУС 3 |  |
| `dicor_v_kdtr_04_mm` | В КДТР 4 | GM | lv_geometry | numeric_continuous | mm | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В КДТР 4 |  |
| `dicor_v_ous_04_pct` | В ОУС 4 | GM | lv_geometry | numeric_continuous | % | geometry_outcome_or_mediator | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | LV geometry / morphometry variable: В ОУС 4 |  |
| `dicor_cv_sfu_at_ksk_lv_pct` | Cv СФУ НА КСК ЛЖ | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: Cv СФУ НА КСК ЛЖ |  |
| `dicor_cv_sfu_at_ksk_regional_pct` | Cv СФУ НА КСК Рег | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: Cv СФУ НА КСК Рег |  |
| `dicor_cv_velocity_pct` | Cv скоростей | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: Cv скоростей |  |
| `dicor_cv_vmax_pct` | Cv Vmax | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: Cv Vmax |  |
| `dicor_delta_t_ms` | d Т | Reg_Mech | regional_mechanics_dicor | numeric_continuous | ms | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: d Т |  |
| `dicor_real_ejection_fraction_pct` | ФИ РЕАЛЬНАЯ | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ФИ РЕАЛЬНАЯ |  |
| `dicor_potential_ejection_fraction_pct` | ФИ  ПОТЕНЦИАЛЬНАЯ | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ФИ  ПОТЕНЦИАЛЬНАЯ |  |
| `dicor_delta_ejection_fraction_pct` | d ФИ | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: d ФИ |  |
| `dicor_ssou_01_pct` | ССОУ1 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ1 |  |
| `dicor_ssou_02_pct` | ССОУ2 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ2 |  |
| `dicor_ssou_03_pct` | ССОУ3 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ3 |  |
| `dicor_ssou_04_pct` | ССОУ4 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ4 |  |
| `dicor_ssou_05_pct` | ССОУ5 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ5 |  |
| `dicor_ssou_06_pct` | ССОУ6 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ6 |  |
| `dicor_ssou_07_pct` | ССОУ7 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ7 |  |
| `dicor_ssou_08_pct` | ССОУ8 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ8 |  |
| `dicor_ssou_09_pct` | ССОУ9 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ9 |  |
| `dicor_ssou_10_pct` | ССОУ10 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ10 |  |
| `dicor_ssou_11_pct` | ССОУ11 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ11 |  |
| `dicor_ssou_12_pct` | ССОУ12 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: ССОУ12 |  |
| `dicor_sfu_at_ksk_lv_01_pct` | СФУ на КСК ЛЖ 1 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 1 |  |
| `dicor_sfu_at_ksk_lv_02_pct` | СФУ на КСК ЛЖ 2 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 2 |  |
| `dicor_sfu_at_ksk_lv_03_pct` | СФУ на КСК ЛЖ 3 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 3 |  |
| `dicor_sfu_at_ksk_lv_04_pct` | СФУ на КСК ЛЖ 4 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 4 |  |
| `dicor_sfu_at_ksk_lv_05_pct` | СФУ на КСК ЛЖ 5 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 5 |  |
| `dicor_sfu_at_ksk_lv_06_pct` | СФУ на КСК ЛЖ 6 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 6 |  |
| `dicor_sfu_at_ksk_lv_07_pct` | СФУ на КСК ЛЖ 7 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 7 |  |
| `dicor_sfu_at_ksk_lv_08_pct` | СФУ на КСК ЛЖ 8 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 8 |  |
| `dicor_sfu_at_ksk_lv_09_pct` | СФУ на КСК ЛЖ 9 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 9 |  |
| `dicor_sfu_at_ksk_lv_10_pct` | СФУ на КСК ЛЖ 10 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 10 |  |
| `dicor_sfu_at_ksk_lv_11_pct` | СФУ на КСК ЛЖ 11 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 11 |  |
| `dicor_sfu_at_ksk_lv_12_pct` | СФУ на КСК ЛЖ 12 | Reg_Mech | regional_mechanics_dicor | numeric_continuous | % | mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional/mechanical DICOR-related cardiac mechanics variable: СФУ на КСК ЛЖ 12 |  |
| `ecg_p_wave_duration_ms` | P | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: P |  |
| `ecg_pq_interval_ms` | PQ | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: PQ |  |
| `ecg_qrs_duration_ms` | QRS | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: QRS |  |
| `ecg_qt_interval_ms` | QT | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: QT |  |
| `ecg_qtc_interval_ms` | QTc | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: QTc |  |
| `ecg_qtc_delta_ms` | dQTc | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: dQTc |  |
| `ecg_rr_interval_ms` | RR | Electr | ecg | numeric_continuous | ms | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: RR |  |
| `ecg_heart_rate_bpm` | HR | Electr | ecg | numeric_continuous | beats/min | ecg_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | ECG electrical phenotype variable: HR |  |
| `lv_false_tendon_apical_oblique_count` | ЛС апикальные косые | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС апикальные косые |  |
| `lv_false_tendon_apical_transverse_count` | ЛС апикальные поперечные | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС апикальные поперечные |  |
| `lv_false_tendon_mid_oblique_count` | ЛС срединные косые | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС срединные косые | mid_obl |
| `lv_false_tendon_mid_transverse_count` | ЛС срединные поперечные | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС срединные поперечные | mid_trans |
| `lv_false_tendon_mid_and_basal_transverse_count` | Поперечные срединные и базальные ЛС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: Поперечные срединные и базальные ЛС | mid_trans + basal_trans |
| `lv_false_tendon_basal_oblique_count` | ЛС базальные косые | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС базальные косые | basal_obl |
| `lv_false_tendon_basal_transverse_count` | ЛС базальные поперечные | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС базальные поперечные | basal_trans |
| `lv_false_tendon_mid_to_basal_oblique_count` | ЛС между срединным и базальным уровнями | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС между срединным и базальным уровнями | basal_mid_obl |
| `lv_false_tendon_mid_to_apical_oblique_count` | ЛС между срединным и апикальным уровнями | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС между срединным и апикальным уровнями | mid_apical_obl |
| `lv_false_tendon_basal_to_apical_oblique_count` | ЛС между базальным и апикальным уровнями | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС между базальным и апикальным уровнями | basal_apical_obl |
| `lv_false_tendon_total_count` | ЛС Общее количество хорд | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛС Общее количество хорд |  |
| `lv_false_tendon_pattern_sbza_count` | СБЗА | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: СБЗА |  |
| `lv_false_tendon_pattern_sbla_count` | СБЛА | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: СБЛА |  |
| `lv_false_tendon_pattern_ssz_count` | ССЗ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ССЗ |  |
| `lv_false_tendon_pattern_ssl_count` | ССЛ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ССЛ |  |
| `lv_false_tendon_pattern_ssza_count` | ССЗА | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ССЗА |  |
| `lv_false_tendon_pattern_ssla_count` | ССЛА | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ССЛА |  |
| `lv_false_tendon_pattern_sbzs_count` | СБЗС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: СБЗС |  |
| `lv_false_tendon_pattern_sbls_count` | СБЛС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: СБЛС |  |
| `lv_false_tendon_pattern_pb_count` | ПБ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ПБ |  |
| `lv_false_tendon_anterior_count` | ПЕРЕДНИЕ ЛС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ПЕРЕДНИЕ ЛС |  |
| `significant_lv_false_tendon_without_anterior_count` | ЗНАЧИМЫЕ ЛС БЕЗ ПЕРЕДНИХ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЗНАЧИМЫЕ ЛС БЕЗ ПЕРЕДНИХ |  |
| `lv_false_tendon_posterior_count` | ЗАДНИЕ ЛС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЗАДНИЕ ЛС |  |
| `significant_lv_false_tendon_without_posterior_count` | ЗНАЧИМЫЕ ЛС БЕЗ ЗАДНИХ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЗНАЧИМЫЕ ЛС БЕЗ ЗАДНИХ |  |
| `lv_false_tendon_lateral_count` | ЛАТЕРАЛЬНЫЕ ЛС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЛАТЕРАЛЬНЫЕ ЛС |  |
| `significant_lv_false_tendon_without_lateral_count` | ЗНАЧИМЫЕ ЛС БЕЗ ЛАТЕРАЛЬНЫХ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЗНАЧИМЫЕ ЛС БЕЗ ЛАТЕРАЛЬНЫХ |  |
| `significant_lv_false_tendon_count` | ЗНАЧИМЫЕ ЛС | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЗНАЧИМЫЕ ЛС |  |
| `lv_false_tendon_basal_to_apical_oblique_count` | БАЗ-АПИК | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: БАЗ-АПИК | basal_apical_obl |
| `lv_false_tendon_mid_to_apical_oblique_count` | СРЕД-АПИК | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: СРЕД-АПИК | mid_apical_obl |
| `lv_false_tendon_basal_to_mid_oblique_count` | БАЗ-СРЕД | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: БАЗ-СРЕД | basal_mid_obl |
| `lv_false_tendon_basal_total_count` | БАЗАЛЬНЫЕ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: БАЗАЛЬНЫЕ | basal_trans + basal_obl |
| `lv_false_tendon_mid_total_count` | СРЕДИННЫЕ | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: СРЕДИННЫЕ | mid_trans + mid_obl |
| `significant_lv_chord_bp_count` | ЗНАЧИМЫЕ ХОРДЫ (БП) | Chords | chord_phenotype | integer | count | primary_predictor | integer ≥0; 0 is valid | TBD after data audit; do not treat 0 as missing for count/flag variables | False LV chord phenotype descriptor: ЗНАЧИМЫЕ ХОРДЫ (БП) |  |
| `exercise_peak_heart_rate_bpm` | ЧСС НАГР | Work | exercise_test | numeric_continuous | beats/min | exercise_covariate_or_secondary_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Exercise/load-test physiology variable: ЧСС НАГР |  |
| `exercise_peak_systolic_bp_mmhg` | САД НАГР | Work | exercise_test | numeric_continuous | mmHg | exercise_covariate_or_secondary_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Exercise/load-test physiology variable: САД НАГР |  |
| `exercise_peak_diastolic_bp_mmhg` | ДАД НАГР | Work | exercise_test | numeric_continuous | mmHg | exercise_covariate_or_secondary_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Exercise/load-test physiology variable: ДАД НАГР |  |
| `exercise_heart_rate_recovery_5min_bpm` | ЧСС 5 минута восстановления | Work | exercise_test | numeric_continuous | beats/min | exercise_covariate_or_secondary_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Exercise/load-test physiology variable: ЧСС 5 минута восстановления |  |
| `exercise_robinson_index` | ИР | Work | exercise_test | TBD | TBD | exercise_covariate_or_secondary_outcome | TBD | TBD after data audit; do not treat 0 as missing for count/flag variables | Exercise/load-test physiology variable: ИР |  |
| `exercise_chronotropic_reserve_pct` | ХР | Work | exercise_test | numeric_continuous | % | exercise_covariate_or_secondary_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Exercise/load-test physiology variable: ХР |  |
| `strain_plus_basal_anteroseptal_strain_pct` | BAS_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BAS_strain_percent |  |
| `strain_plus_basal_anteroseptal_strain_rate_1_s` | BAS_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BAS_strain_sr_1_s |  |
| `strain_plus_basal_anteroseptal_time_to_peak_strain_ms` | BAS_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BAS_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_basal_anterior_strain_pct` | BA_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BA_strain_percent |  |
| `strain_plus_basal_anterior_strain_rate_1_s` | BA_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BA_strain_sr_1_s |  |
| `strain_plus_basal_anterior_time_to_peak_strain_ms` | BA_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BA_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_basal_anterolateral_strain_pct` | BAL_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BAL_strain_percent |  |
| `strain_plus_basal_anterolateral_strain_rate_1_s` | BAL_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BAL_strain_sr_1_s |  |
| `strain_plus_basal_anterolateral_time_to_peak_strain_ms` | BAL_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BAL_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_basal_inferolateral_strain_pct` | BIL_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BIL_strain_percent |  |
| `strain_plus_basal_inferolateral_strain_rate_1_s` | BIL_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BIL_strain_sr_1_s |  |
| `strain_plus_basal_inferolateral_time_to_peak_strain_ms` | BIL_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BIL_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_basal_inferior_strain_pct` | BI_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BI_strain_percent |  |
| `strain_plus_basal_inferior_strain_rate_1_s` | BI_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BI_strain_sr_1_s |  |
| `strain_plus_basal_inferior_time_to_peak_strain_ms` | BI_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BI_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_basal_inferoseptal_strain_pct` | BIS_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BIS_strain_percent |  |
| `strain_plus_basal_inferoseptal_strain_rate_1_s` | BIS_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BIS_strain_sr_1_s |  |
| `strain_plus_basal_inferoseptal_time_to_peak_strain_ms` | BIS_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: BIS_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_mid_anteroseptal_strain_pct` | MAS_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MAS_strain_percent |  |
| `strain_plus_mid_anteroseptal_strain_rate_1_s` | MAS_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MAS_strain_sr_1_s |  |
| `strain_plus_mid_anteroseptal_time_to_peak_strain_ms` | MAS_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MAS_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_mid_anterior_strain_pct` | MA_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MA_strain_percent |  |
| `strain_plus_mid_anterior_strain_rate_1_s` | MA_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MA_strain_sr_1_s |  |
| `strain_plus_mid_anterior_time_to_peak_strain_ms` | MA_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MA_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_mid_anterolateral_strain_pct` | MAL_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MAL_strain_percent |  |
| `strain_plus_mid_anterolateral_strain_rate_1_s` | MAL_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MAL_strain_sr_1_s |  |
| `strain_plus_mid_anterolateral_time_to_peak_strain_ms` | MAL_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MAL_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_mid_inferolateral_strain_pct` | MIL_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MIL_strain_percent |  |
| `strain_plus_mid_inferolateral_strain_rate_1_s` | MIL_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MIL_strain_sr_1_s |  |
| `strain_plus_mid_inferolateral_time_to_peak_strain_ms` | MIL_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MIL_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_mid_inferior_strain_pct` | MI_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MI_strain_percent |  |
| `strain_plus_mid_inferior_strain_rate_1_s` | MI_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MI_strain_sr_1_s |  |
| `strain_plus_mid_inferior_time_to_peak_strain_ms` | MI_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MI_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_mid_inferoseptal_strain_pct` | MIS_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MIS_strain_percent |  |
| `strain_plus_mid_inferoseptal_strain_rate_1_s` | MIS_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MIS_strain_sr_1_s |  |
| `strain_plus_mid_inferoseptal_time_to_peak_strain_ms` | MIS_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: MIS_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_apical_anteroseptal_strain_pct` | AAS_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AAS_strain_percent |  |
| `strain_plus_apical_anteroseptal_strain_rate_1_s` | AAS_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AAS_strain_sr_1_s |  |
| `strain_plus_apical_anteroseptal_time_to_peak_strain_ms` | AAS_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AAS_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_apical_anterior_strain_pct` | AA_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AA_strain_percent |  |
| `strain_plus_apical_anterior_strain_rate_1_s` | AA_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AA_strain_sr_1_s |  |
| `strain_plus_apical_anterior_time_to_peak_strain_ms` | AA_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AA_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_apical_anterolateral_strain_pct` | AAL_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AAL_strain_percent |  |
| `strain_plus_apical_anterolateral_strain_rate_1_s` | AAL_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AAL_strain_sr_1_s |  |
| `strain_plus_apical_anterolateral_time_to_peak_strain_ms` | AAL_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AAL_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_apical_inferolateral_strain_pct` | AIL_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AIL_strain_percent |  |
| `strain_plus_apical_inferolateral_strain_rate_1_s` | AIL_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AIL_strain_sr_1_s |  |
| `strain_plus_apical_inferolateral_time_to_peak_strain_ms` | AIL_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AIL_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_apical_inferior_strain_pct` | AI_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AI_strain_percent |  |
| `strain_plus_apical_inferior_strain_rate_1_s` | AI_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AI_strain_sr_1_s |  |
| `strain_plus_apical_inferior_time_to_peak_strain_ms` | AI_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AI_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_apical_inferoseptal_strain_pct` | AIS_strain_percent | Strein | regional_strain_ste | numeric_continuous | % | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AIS_strain_percent |  |
| `strain_plus_apical_inferoseptal_strain_rate_1_s` | AIS_strain_sr_1_s | Strein | regional_strain_ste | numeric_continuous | 1/s | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AIS_strain_sr_1_s |  |
| `strain_plus_apical_inferoseptal_time_to_peak_strain_ms` | AIS_strain_Time_to_Peak_Strain_ms | Strein | regional_strain_ste | numeric_continuous | ms | regional_mechanics_outcome | physiological numeric range; define after audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Regional STE-derived LV mechanics variable: AIS_strain_Time_to_Peak_Strain_ms |  |
| `strain_plus_basal_anteroseptal_chord_attachment_flag` | BAS_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: BAS_chord_attachment |  |
| `strain_plus_basal_anterior_chord_attachment_flag` | BA_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: BA_chord_attachment |  |
| `strain_plus_basal_anterolateral_chord_attachment_flag` | BAL_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: BAL_chord_attachment |  |
| `strain_plus_basal_inferolateral_chord_attachment_flag` | BIL_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: BIL_chord_attachment |  |
| `strain_plus_basal_inferior_chord_attachment_flag` | BI_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: BI_chord_attachment |  |
| `strain_plus_basal_inferoseptal_chord_attachment_flag` | BIS_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: BIS_chord_attachment |  |
| `strain_plus_mid_anteroseptal_chord_attachment_flag` | MAS_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: MAS_chord_attachment |  |
| `strain_plus_mid_anterior_chord_attachment_flag` | MA_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: MA_chord_attachment |  |
| `strain_plus_mid_anterolateral_chord_attachment_flag` | MAL_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: MAL_chord_attachment |  |
| `strain_plus_mid_inferolateral_chord_attachment_flag` | MIL_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: MIL_chord_attachment |  |
| `strain_plus_mid_inferior_chord_attachment_flag` | MI_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: MI_chord_attachment |  |
| `strain_plus_mid_inferoseptal_chord_attachment_flag` | MIS_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: MIS_chord_attachment |  |
| `strain_plus_apical_anteroseptal_chord_attachment_flag` | AAS_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: AAS_chord_attachment |  |
| `strain_plus_apical_anterior_chord_attachment_flag` | AA_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: AA_chord_attachment |  |
| `strain_plus_apical_anterolateral_chord_attachment_flag` | AAL_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: AAL_chord_attachment |  |
| `strain_plus_apical_inferolateral_chord_attachment_flag` | AIL_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: AIL_chord_attachment |  |
| `strain_plus_apical_inferior_chord_attachment_flag` | AI_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: AI_chord_attachment |  |
| `strain_plus_apical_inferoseptal_chord_attachment_flag` | AIS_chord_attachment | Strein_CHORDS | chord_attachment_topology | binary | 0/1 | derived_topological_predictor | 0/1; confirm coding during audit | TBD after data audit; do not treat 0 as missing for count/flag variables | Segment-level chord attachment marker for topology/local signature: AIS_chord_attachment |  |

---

## 10. Новые derived features, которые нужно добавить позже

После реализации feature engineering сюда нужно добавить переменные следующих групп.

### 10.1. Local mechanical signature

| variable_name | domain | data_type | unit | model_role | biological_meaning |
|---|---|---|---|---|---|
| `insertion_mean_strain_pct` | derived_local_signature | numeric_continuous | % | primary_mechanistic_outcome | Средний strain в сегментах прикрепления хорды |
| `adjacent_mean_strain_pct` | derived_local_signature | numeric_continuous | % | primary_mechanistic_outcome | Средний strain в соседних сегментах |
| `remote_mean_strain_pct` | derived_local_signature | numeric_continuous | % | primary_mechanistic_outcome | Средний strain в удалённых сегментах |
| `insertion_minus_remote_strain_pct` | derived_local_signature | numeric_continuous | % | primary_mechanistic_outcome | Локальный контраст insertion vs remote |
| `insertion_minus_adjacent_strain_pct` | derived_local_signature | numeric_continuous | % | primary_mechanistic_outcome | Локальный контраст insertion vs adjacent |

### 10.2. Spatial gradient

| variable_name | domain | data_type | unit | model_role | biological_meaning |
|---|---|---|---|---|---|
| `strain_gradient_slope` | derived_spatial_gradient | numeric_continuous | % per distance unit | primary_mechanistic_outcome | Наклон изменения strain по мере удаления от хорды |
| `time_to_peak_gradient_slope` | derived_spatial_gradient | numeric_continuous | ms per distance unit | primary_mechanistic_outcome | Наклон изменения времени пика deformation по расстоянию от хорды |
| `gradient_magnitude` | derived_spatial_gradient | numeric_continuous | standardized | supportive_outcome | Выраженность spatial gradient |
| `gradient_direction` | derived_spatial_gradient | categorical | category | supportive_outcome | Направление градиента |

### 10.3. Topological features

| variable_name | domain | data_type | unit | model_role | biological_meaning |
|---|---|---|---|---|---|
| `graph_distance_to_chord` | derived_topology | integer | graph steps | derived_topological_predictor | Расстояние сегмента до ближайшей зоны прикрепления хорды |
| `is_chord_connected_segment` | derived_topology | binary | 0/1 | derived_topological_predictor | Сегмент является точкой прикрепления хорды |
| `is_adjacent_to_chord_segment` | derived_topology | binary | 0/1 | derived_topological_predictor | Сегмент соседствует с зоной прикрепления |
| `is_remote_segment` | derived_topology | binary | 0/1 | derived_topological_predictor | Сегмент удалён от хорды |
| `mechanical_coupling_connected_segments` | derived_topology | numeric_continuous | TBD | exploratory_outcome | Согласованность механики сегментов, соединённых хордой |

---

## 11. Update protocol

При изменении словаря:

1. Не удалять старое значение без комментария.
2. Добавлять причину изменения в `notes`.
3. Если изменилось имя переменной, сохранить старое имя в `analogue`.
4. Если переменная исключена, указать причину.
5. Если переменная стала derived, указать формулу или источник.
6. Синхронизировать изменения с:
   - `docs/ANALYSIS_PLAN.md`;
   - `docs/DATA_PROVENANCE.md`;
   - `params.yaml`;
   - `config/variables.yml`, если он будет создан.

---

## 12. Short rule

Переменная не должна использоваться в confirmatory analysis, если для неё неизвестны:

```text
meaning
domain
type
unit
model role
allowed values
missing codes
quality rules
```
