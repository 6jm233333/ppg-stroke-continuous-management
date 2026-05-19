# Reproducibility guide

## Reproducibility levels

Because source clinical and waveform datasets are restricted, reproducibility has multiple levels.

| Level | What can be reproduced | Required access |
|---|---|---|
| Documentation review | Study design, assumptions, claim boundaries, release checks | None |
| Figure/table regeneration | Manuscript tables and figures from non-identifiable derived summaries | Curated derived summaries permitted for sharing |
| Full computational reproduction | Cohorts, anchors, PPG features, model training, external validation | Authorized access to MIMIC-III, MC-MED, and project anchor manifests |
| Independent clinical validation | Evaluation in a new clinical environment | Local ethics, data-use approval, and independent temporal anchors |

## Required inputs for full reproduction

Full reproduction requires local, access-controlled copies of:

- MIMIC-III waveform and structured clinical data.
- MC-MED waveform and structured clinical data.
- Clinically anchored stroke-recognition manifests.
- Prognosis trajectory labels.
- PPG waveform reference manifests.
- Feature-extraction configuration and quality-filter settings.
- Frozen model and preprocessing configurations for external validation.

Do not place these files under Git version control.

## Recommended execution order

1. Validate local data paths and access permissions.
2. Build cohort manifests for the warning and prognosis tasks.
3. Link waveform records to patient, admission, and event timelines.
4. Construct warning windows at 4, 5, and 6 h before the recognition anchor.
5. Apply transition-buffer and lead-time blind-zone exclusions.
6. Process retained PPG segments through the morphology pipeline.
7. Build baseline-relative features for the warning task.
8. Train MIMIC-III internal models using patient-level or group-aware cross-validation.
9. Freeze preprocessing, selected thresholds, and model checkpoints.
10. Evaluate MC-MED external validation without retuning or recalibration.
11. Generate structured EHR baseline results using horizon-appropriate covariates.
12. Generate SHAP interpretation, signal-quality, subgroup, and falsification analyses.
13. Rebuild manuscript tables and figures from scripted outputs.

## Split and leakage safeguards

The following checks are mandatory:

- No patient appears in more than one fold for the warning task.
- No grouped hospitalization or subject leaks across folds in the prognosis task.
- MC-MED is never used for model selection, threshold optimization, or recalibration.
- Lead-time blind-zone windows are excluded from warning training and evaluation.
- Structured EHR baseline variables are restricted to information available before the relevant horizon.
- PPG signal-quality or retention indicators are not used as prediction features unless explicitly defined as a separate sensitivity analysis.

## Determinism and audit trails

Each reproducible run should record:

- Git commit hash.
- Configuration file hash.
- Source manifest hash.
- Random seed values.
- Package versions.
- Dataset release/version identifiers.
- Model checkpoint identifiers.
- Output directory and timestamp.

## What not to do

- Do not tune on MC-MED.
- Do not use event-specific negative controls without validated event-anchor timing.
- Do not infer minute-level event anchors from diagnosis summaries.
- Do not report pseudo-anchor performance as robustness or specificity evidence.
- Do not combine patient-level windows across splits.