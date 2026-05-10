# GEMINI.md

## Project identity

This repository supports a dissertation-level biomedical research project on the physiological and mechanical role of **left ventricular false chords / false tendons**.

The project is not a routine statistical screening task. It is a mechanistic research project focused on how intracavitary structures of the left ventricle may be associated with regional myocardial mechanics, LV geometry, LV function, and ECG characteristics.

Project root on the user's machine:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res
```

Main analysis dataset:

```text
C:\Users\Ars\projects\university\lab_urfu_2026\fh_res\data\final_analysis_dataset.xlsx
```

Expected scale:

```text
n ≈ 200 participants
p ≈ 240 variables
```

Primary language for communication with the user: **Russian**.  
Code, variable names, file names, and technical identifiers should preferably remain in **English**.

---

## Research framing

The central research idea is:

> False chords of the left ventricle should be treated not merely as anatomical findings, but as potential **internal mechanical constraints** that may modify local and regional LV mechanics.

The project should avoid a simplistic comparison:

```text
false chord present vs absent
```

Instead, analysis should focus on:

```text
chord mechanical phenotype → regional mechanics / geometry / function / ECG
```

Key conceptual layers:

1. **False chord as internal mechanical constraint**
   - The chord may act as an intracavitary mechanical link.
   - It may constrain local deformation, alter segmental strain patterns, or redistribute mechanical load.

2. **Regional mechanics rather than EF**
   - Ejection fraction is not the main target.
   - EF may remain normal despite regional mechanical differences.
   - Prioritize strain, strain rate, segmental mechanics, dyssynchrony-like patterns, deformation gradients, and mechanical heterogeneity.

3. **Chord mechanical phenotype**
   - Presence/absence is secondary.
   - Important descriptors include:
     - localization;
     - orientation;
     - attachment points;
     - number of chords;
     - segment-to-segment connection;
     - basal/mid/apical relation;
     - septal/free-wall relation;
     - longitudinal/transverse/oblique direction;
     - possible topological role as a link between LV segments.

4. **Local mechanical signature**
   - Compare regions directly related to the chord with anatomically adjacent and remote regions:
     - insertion segments;
     - adjacent segments;
     - remote segments.

5. **Spatial gradient**
   - Test whether the effect is strongest at insertion zones, weaker in adjacent regions, and minimal in remote regions.
   - Prefer models that preserve spatial interpretation.

6. **Topological approach**
   - A chord can be encoded as a connection between LV segments.
   - Treat the LV as a segmental graph where the chord adds an internal edge.
   - Explore whether segmental mechanics differ according to graph distance from chord insertion.

---

## Scientific tone and interpretation

Maintain a postdoc / research-grade level of reasoning.

Avoid phrases that imply causality unless the design supports it. Prefer:

```text
associated with
compatible with the hypothesis
consistent with a mechanical constraint model
suggests a regional mechanical signature
```

Avoid unsupported claims such as:

```text
false chords cause dysfunction
false chords impair cardiac function
false chords are pathological
```

Correct framing:

```text
False chord phenotypes are associated with regional mechanical patterns after adjustment for relevant covariates.
```

or:

```text
The observed associations are compatible with the hypothesis that false chords act as internal mechanical constraints influencing regional LV mechanics.
```

---

## Main analytical principle

Do not run 240 variables through arbitrary pairwise tests.

The correct logic is:

```text
domain structure → dimensionality reduction / structured features → adjusted models → stability → sensitivity → mechanistic interpretation
```

Recommended high-level pipeline:

1. Define variable roles:
   - chord predictors;
   - covariates/confounders;
   - mechanics outcomes;
   - geometry outcomes;
   - function outcomes;
   - ECG outcomes;
   - derived regional/topological features.

2. Define domain blocks:
   - chord phenotype;
   - LV mechanics / strain;
   - LV geometry;
   - LV global function;
   - ECG;
   - anthropometry / demographics;
   - sport or training-related variables if available.

3. Perform data validation and audit:
   - missingness;
   - duplicates;
   - impossible values;
   - coding inconsistencies;
   - outliers;
   - distribution diagnostics;
   - variable type validation.

4. Build interpretable derived features:
   - insertion-region strain;
   - adjacent-region strain;
   - remote-region strain;
   - insertion-minus-remote contrast;
   - spatial gradient;
   - mechanical heterogeneity;
   - segmental dispersion;
   - chord graph distance;
   - domain-level PCA scores.

5. Test block-level hypotheses first.

6. Only after block-level evidence, inspect individual variables.

7. Always assess robustness:
   - bootstrap;
   - permutation;
   - FDR by variable families;
   - stability selection;
   - sensitivity models;
   - influence diagnostics.

---

## Variable role rules

Never assume that all variables are independent predictors.

Possible roles:

### Chord predictors

Examples:

```text
false_chord_presence
false_chord_count
false_chord_type
false_chord_orientation
false_chord_attachment_1
false_chord_attachment_2
false_chord_segment_from
false_chord_segment_to
false_chord_length
false_chord_thickness
false_chord_basal_mid_apical_location
```

Use actual dataset column names only after inspecting the data dictionary or dataset.

### Core covariates

Expected baseline covariates may include:

```text
age
sex
height
weight
BSA
sport
training_level
diagnosis_or_group
heart_rate
blood_pressure
```

Do not automatically adjust for every available variable.

Important rule:

If a variable may lie on the pathway

```text
false chord → LV geometry → strain → EF / ECG
```

then it may be a mediator, not a confounder. Do not adjust for potential mediators in the primary model unless the model is explicitly defined as mediation/sensitivity analysis.

### Outcomes

Outcome domains may include:

```text
regional strain
global strain
strain rate
time to peak strain
LV geometry
LV volumes
LV mass
EF
diastolic parameters
ECG intervals
ECG conduction markers
repolarization markers
```

EF should not be treated as the primary marker of subtle mechanical effects.

---

## Preferred statistical strategy

### 1. Descriptive and data audit layer

Required outputs:

```text
reports/tables/data_dictionary_audit.xlsx
reports/tables/missingness_summary.xlsx
reports/tables/descriptive_statistics.xlsx
reports/figures/missingness_heatmap.png
reports/figures/domain_correlation_heatmap.png
reports/figures/outlier_diagnostics.png
```

Focus on whether the dataset is scientifically analyzable, not only technically valid.

### 2. Domain PCA

Use PCA within conceptually coherent domains, for example:

```text
mechanics domain
geometry domain
function domain
ECG domain
```

Do not run one global PCA over all variables without physiological justification.

Interpret PCA loadings physiologically:

```text
PC1_mechanics = global deformation axis
PC2_mechanics = regional heterogeneity axis
PC1_geometry = LV size/remodeling axis
PC2_geometry = shape/proportionality axis
```

Use PCA only after:

```text
scaling;
missing data handling;
domain-specific variable filtering;
checking correlation structure;
documenting explained variance.
```

### 3. Block-level models

Primary question:

```text
Do chord phenotype variables explain variation in cardiac domains beyond covariates?
```

Compare nested models:

```text
Base model:
cardiac_domain ~ age + sex + BSA + other justified covariates

Chord model:
cardiac_domain ~ age + sex + BSA + chord_phenotype
```

Report:

```text
ΔR² / adjusted ΔR²
cross-validated performance difference
permutation p-value if appropriate
bootstrap confidence interval
effect direction
stability
```

### 4. Regional/local models

Primary mechanistic model:

```text
regional_mechanics ~ chord_insertion_status + distance_from_chord + covariates
```

Possible derived contrasts:

```text
insertion_mean_strain
adjacent_mean_strain
remote_mean_strain
insertion_minus_remote
insertion_minus_adjacent
adjacent_minus_remote
spatial_gradient_slope
mechanical_dispersion
```

Prioritize interpretable effect sizes over isolated p-values.

### 5. Penalized models

Use Elastic Net when predictors are correlated.

Purpose:

```text
feature selection stability
incremental predictive signal of chord variables
identification of candidate mechanical phenotype markers
```

Avoid using Elastic Net as the only evidence.

Recommended outputs:

```text
selected_features_by_bootstrap.csv
selection_frequency.csv
coefficient_stability.csv
model_comparison_base_vs_chord.csv
```

### 6. Sparse PLS

Use sparse PLS to identify multivariate associations between:

```text
X = chord phenotype block
Y = cardiac mechanics / geometry / ECG block
```

Interpret as latent covariance structure, not causality.

Good interpretation format:

```text
A chord phenotype pattern characterized by [features] was associated with a cardiac pattern characterized by [regional strain/geometry/ECG features].
```

### 7. Bayesian shrinkage

Use Bayesian shrinkage models only for selected confirmatory candidate hypotheses, not as the first exploratory step.

Possible use:

```text
Bayesian regression with weakly informative or shrinkage priors
Bayesian hierarchical model for segmental mechanics
posterior probability of direction
credible intervals
```

Report:

```text
posterior mean
95% credible interval
probability of positive/negative direction
practical effect size
```

---

## Multiple testing and robustness

Do not rely on isolated p-values.

Required robustness concepts:

```text
bootstrap stability
permutation testing
FDR correction by outcome family
sensitivity analysis
influence diagnostics
outlier robustness
alternative covariate sets
```

FDR should be controlled within meaningful families:

```text
strain family
geometry family
function family
ECG family
regional contrast family
```

Avoid one massive FDR correction across unrelated variables if it destroys interpretability.

---

## Mechanistic interpretation rules

Every statistical result should be translated into a physiological statement.

Bad:

```text
Variable X was significant with p = 0.031.
```

Better:

```text
The association between oblique basal-to-mid false chord phenotype and reduced regional deformation near insertion zones suggests a localized mechanical constraint pattern rather than a global systolic dysfunction pattern.
```

Always distinguish:

```text
global function
regional deformation
mechanical heterogeneity
geometry/remodeling
electrical markers
```

Do not over-interpret small effects. For weak but stable effects, say:

```text
The effect is modest in magnitude but directionally stable across resampling procedures.
```

---

## Project structure

Recommended repository layout:

```text
fh_res/
│
├── GEMINI.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── interim/
│   └── final_analysis_dataset.xlsx
│
├── config/
│   ├── variables.yml
│   ├── domains.yml
│   ├── covariates.yml
│   ├── analysis_plan.yml
│   └── paths.yml
│
├── src/
│   └── fh_res/
│       ├── __init__.py
│       ├── data/
│       ├── validation/
│       ├── features/
│       ├── domains/
│       ├── models/
│       ├── stability/
│       ├── visualization/
│       └── reporting/
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_domain_eda.ipynb
│   ├── 03_primary_models.ipynb
│   ├── 04_regional_mechanics.ipynb
│   └── 05_figures_for_manuscript.ipynb
│
├── scripts/
│   ├── run_data_audit.py
│   ├── run_feature_engineering.py
│   ├── run_primary_analysis.py
│   ├── run_stability_analysis.py
│   └── build_report.py
│
├── reports/
│   ├── figures/
│   ├── tables/
│   ├── diagnostics/
│   └── manuscript/
│
├── docs/
│   ├── research_protocol.md
│   ├── statistical_analysis_plan.md
│   ├── variable_dictionary.md
│   ├── data_quality_report.md
│   └── agent_notes.md
│
└── tests/
    ├── test_data_validation.py
    ├── test_feature_engineering.py
    ├── test_domain_config.py
    └── test_model_outputs.py
```

Do not create all files at once unless requested. Build incrementally.

---

## Coding standards

Use Python for analysis.

Preferred stack:

```text
pandas
numpy
scipy
statsmodels
scikit-learn
openpyxl
matplotlib
seaborn only if explicitly allowed by the user
pydantic
pyyaml
pingouin if useful
pymc / bambi only for Bayesian layer if needed
```

General rules:

1. Keep code modular.
2. Avoid large monolithic notebooks.
3. Put reusable logic in `src/fh_res/`.
4. Use notebooks mainly for exploration and narrative review of results.
5. Every script should be runnable from project root.
6. Use relative paths through config files.
7. Do not hardcode absolute Windows paths inside analysis modules unless there is no alternative.
8. Do not overwrite raw data.
9. Save all generated outputs into `reports/`, `data/interim/`, or `data/processed/`.
10. Add logging for long-running scripts.

---

## Data safety

The dataset is biomedical and should be treated as sensitive.

Rules:

```text
Do not expose personal data.
Do not print full names or identifiers into logs.
Do not commit raw data.
Do not include raw participant-level data in generated examples.
Do not create public synthetic data by merely perturbing real rows.
```

If identifiers are present, use:

```text
participant_id
study_id
anonymous_id
```

Never use names as merge keys in final analytical outputs.

---

## Output standards

For every analysis script, generate machine-readable and human-readable outputs.

Preferred formats:

```text
.xlsx for tables intended for dissertation/manuscript
.csv for pipeline outputs
.png or .svg for figures
.md for reports and summaries
.json or .yml for metadata/manifests
```

Every important run should save a manifest:

```text
reports/diagnostics/run_manifest.json
```

The manifest should include:

```text
timestamp
input dataset path
dataset shape
selected variables
excluded variables
covariates
models
random seed
software versions
output files
warnings
```

---

## Figure standards

Figures should be publication-ready.

Rules:

1. Use clear labels.
2. Avoid decorative styling.
3. Prefer interpretable plots:
   - coefficient plots;
   - bootstrap interval plots;
   - PCA loading plots;
   - explained variance plots;
   - heatmaps by domain;
   - regional LV segment maps if possible;
   - insertion/adjacent/remote contrast plots;
   - stability selection frequency plots.

4. Every figure should answer a scientific question.

Bad figure:

```text
random pairplot of all variables
```

Good figure:

```text
Spatial gradient of strain difference from chord insertion to remote segments
```

---

## Manuscript logic

The project should support publication-level outputs.

Preferred paper narrative:

1. False chords are usually treated as incidental findings.
2. Standard global LV function may not capture subtle mechanical consequences.
3. Speckle tracking and regional mechanics allow analysis of local deformation patterns.
4. False chords can be conceptualized as internal mechanical constraints.
5. The study tests whether chord mechanical phenotype is associated with:
   - regional strain;
   - spatial deformation gradients;
   - LV geometry;
   - ECG markers.
6. Robustness is assessed through adjusted models, bootstrap, stability selection, and sensitivity analysis.
7. The final interpretation is mechanistic but cautious.

---

## What not to do

Do not:

```text
run blind correlations across all variables;
treat p < 0.05 as the main result;
use deep learning for n≈200 tabular data;
claim causality from cross-sectional associations;
treat EF as the central endpoint;
ignore covariates;
ignore multiple testing;
mix predictors, mediators, and outcomes without a DAG;
create unreadable notebooks with all logic inside cells;
overwrite source data;
invent column names without checking the dataset.
```

---

## Agent workflow

When asked to modify or create code:

1. Inspect existing files first.
2. Identify the smallest safe change.
3. Preserve current project structure.
4. Add or update tests when appropriate.
5. Save outputs in the expected folders.
6. Explain what changed in Russian.
7. Mention assumptions explicitly.
8. Do not silently change the scientific logic.

When asked to create a new analysis:

1. Define the scientific question.
2. Define predictors, outcomes, covariates, and exclusions.
3. Check whether variables exist.
4. Run data quality checks.
5. Fit the simplest justified model first.
6. Add robustness layer.
7. Save results.
8. Interpret physiologically.

When uncertain:

```text
Do not guess.
Inspect the dataset, config, or existing documentation.
If still uncertain, ask the user briefly in Russian.
```

---

## Recommended first project files

After this `GEMINI.md`, useful next files are:

```text
README.md
config/paths.yml
config/domains.yml
config/covariates.yml
config/analysis_plan.yml
docs/research_protocol.md
docs/statistical_analysis_plan.md
docs/variable_dictionary.md
scripts/run_data_audit.py
```

---

## User preferences

The user expects:

```text
high-level scientific reasoning;
mechanistic interpretation;
publication-oriented logic;
practical implementation guidance;
clear Russian explanations;
structured project organization;
reproducible analytical pipeline;
strong statistical guardrails;
no banal methods;
no superficial "run everything through ML" approach.
```

The assistant should proactively suggest improvements when the project structure, analysis logic, or reproducibility can be improved.
