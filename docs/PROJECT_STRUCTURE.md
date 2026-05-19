# Project structure

The repository is organized to separate reusable code, scripts, configuration, documentation, and non-identifiable release assets.

```text
Code/
  README.md
  CITATION.cff
  CHANGELOG.md
  CONTRIBUTING.md
  LICENSE_PENDING.md
  .gitignore
  configs/
    paths.example.yaml
    study.example.yaml
  docs/
    README.md
    DATA_ACCESS.md
    ENVIRONMENT.md
    MANUSCRIPT_ALIGNMENT.md
    METHODS_OVERVIEW.md
    MODEL_CARD.md
    NEGATIVE_CONTROLS.md
    PPG_FEATURES.md
    PROJECT_STRUCTURE.md
    RELEASE_CHECKLIST.md
    REPRODUCIBILITY.md
    RESULTS_REPORTING.md
    SECURITY_AND_PRIVACY.md
  scripts/
    README.md
    rebuild_warning_windows.py
    extract_ppg_features.py
    train_warning_resnet.py
    run_prognosis_external.py
    run_ehr_baseline.py
    run_falsification_inference.py
    make_extended_data_figure.py
  src/
    README.md
    ppg_stroke/
      features/
      models/
      baselines/
      falsification/
      reporting/
  tests/
    README.md
```

## Source code

Reusable modules live in `src/ppg_stroke/`. Workflow orchestration lives in `scripts/`. Notebook logic should be migrated into scripts before publication.

## Configuration

Configuration files should live in `configs/`. They should contain relative names or environment-variable references, not private local paths.

## Results

Only small, non-identifiable, publication-ready summaries should be committed. Raw clinical data, waveform files, derived feature matrices, model checkpoints, and private run artifacts must remain outside Git.

## Tests

Tests should cover:

- warning-window construction,
- lead-time blind-zone exclusion,
- feature-column schema checks,
- prognosis aggregation decision rules,
- no-PHI and no-private-path release scans.
