# Source code provenance

This repository is a cleaned, release-oriented implementation derived from the project's working analysis scripts. The legacy scripts contain private paths, intermediate audit logic and restricted data references; they are not copied verbatim into the public code tree. The table below maps release modules to the real source logic they preserve.

| Release file | Primary source script | Preserved implementation logic |
| --- | --- | --- |
| `src/ppg_stroke/features/windowing.py` | `Step6_Mimic_60_30_labels.py` | Warning labels relative to clinical recognition anchor: stable negative window within 8 h, transition buffer around the warning-horizon boundary, positive warning interval up to the recognition anchor, post-anchor exclusion. |
| `src/ppg_stroke/schemas.py` | `Step6_Mimic_60_30_labels.py`; `Step45_Rebuttal_REL_Residual_Test.py` | Canonical 17 PPG morphology columns and REL/NoREL feature group definitions. |
| `src/ppg_stroke/features/preprocessing.py` | `Step45_Rebuttal_REL_Residual_Test.py`; frozen negative-control script | Yeo-Johnson PowerTransformer preprocessing, constant-column handling, REL residualization against `Time_Rel_Min`, and time-only channel construction. |
| `src/ppg_stroke/models/resnet1d.py` | `Step45_Rebuttal_REL_Residual_Test.py`; frozen negative-control script | ResNet-1D block structure for `[batch, time, features]` PPG morphology tensors. |
| `src/ppg_stroke/models/train_eval.py` | `Step45_Rebuttal_REL_Residual_Test.py` | Weighted cross-entropy training, Adam optimizer, validation-threshold sweep from 0.50 to 1.00, F2/F1 threshold ranking and validation AUC-first model selection. |
| `src/ppg_stroke/models/aggregation.py` | `external_test_from_folds.py` | Full-sequence sliding windows, `max`, `mean` and `consecutive_k` aggregation, longest-run decision rule and sequence-level metrics. |
| `src/ppg_stroke/baselines/ehr.py` | `Step13_EHR_Prognosis_Experiments.py` | Shared MIMIC/MC-MED numeric clinical features, median imputation, RobustScaler, SMOTE, LightGBM/XGBoost/RandomForest search spaces, Youden thresholding and external validation metrics. |
| `src/ppg_stroke/falsification/frozen_inference.py` | frozen negative-control script | Frozen Raw warning model inference, manifest-level `row_start`/`row_end_excl` windows, optional frozen PowerTransformer artifacts, pseudo-anchor inference and patient-level permutation anchor generation. |
| `src/ppg_stroke/reporting/extended_data_fig.py` | paper-ready falsification figure workflow | High-density Extended Data figure rendering from prediction-level pseudo/permutation anchor outputs. |

## Deliberate changes from legacy scripts

- Private absolute paths were removed and replaced with config-driven paths.
- Large raw datasets, feature matrices, model checkpoints and clinical identifiers are excluded from Git.
- Event-specific negative controls are not implemented as a default paper-ready workflow because validated event-anchor timing was insufficient.
- Matched non-stroke control performance claims are not exposed as a main reporting workflow because matching balance was not adequate for specificity claims.
- The warning task is described as a pre-recognition haemodynamic warning signal, not as a stroke-specific diagnostic alert.

## Reproducibility boundary

The code is intended to be executable by authorized users who can provide the same derived manifests, feature tables and checkpoints used in the analysis. It is not a synthetic example project and should not be mixed with unvalidated anchors or summary-only tables.

