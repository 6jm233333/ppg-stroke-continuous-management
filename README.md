# Photoplethysmographic haemodynamic information for continuous stroke management

This repository is prepared to accompany the manuscript **"Photoplethysmographic haemodynamic information for continuous stroke management"**. The project evaluates whether routine photoplethysmography (PPG) waveform morphology provides continuous haemodynamic information for two stroke-care settings:

1. **Pre-recognition warning** before clinically documented in-hospital stroke recognition.
2. **Post-admission prognosis stratification** after stroke-associated hospitalization.

MIMIC-III is used for internal development, and MC-MED is reserved for frozen external validation. The repository documentation is intentionally conservative: the pre-recognition model should be interpreted as a continuous physiological warning layer, not as a stroke-specific diagnostic alert.

## Scientific scope

The project asks whether beat-level PPG morphology contains information that is not fully captured by structured electronic health record (EHR) data. It does not claim that PPG replaces neurological examination, neuroimaging, electrocardiography, laboratory testing, clinical scoring, or structured clinical assessment.

The warning analysis evaluates nominal 4-, 5- and 6-h look-ahead schemes relative to documented clinical recognition. Label construction uses a 15-min transition buffer on each side of the nominal horizon boundary and a separate 15-min recognition-proximal blind zone. Samples acquired within the final 15 min before documented recognition are excluded from both training and evaluation. The prognosis analysis distinguishes improved from worsened-or-deceased clinical trajectories after stroke-associated admission.

## Repository status

This directory contains the manuscript-aligned core code for the PPG stroke warning and prognosis analyses. Source datasets, restricted derived files, and trained checkpoints are not included. The code is organized as reusable Python modules under `src/ppg_stroke` with command-line entry points under `scripts`.

## Repository layout

```text
Code/
|-- README.md
|-- CITATION.cff
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- .gitignore
|-- configs/              # configuration files; no secrets or PHI
|-- docs/                 # method, data, model, and reporting documentation
|-- LICENSE_PENDING.md    # current license status
|-- scripts/              # command-line workflow entry points
|-- src/ppg_stroke/       # reusable warning, prognosis, baseline and figure code
`-- tests/                # unit and smoke tests
```

## Core code

- `src/ppg_stroke/features/windowing.py`: warning-window time-axis reconstruction, 4 h, 5 h and 6 h label assignment, horizon-boundary transition exclusion, and the 15-min recognition-proximal blind zone.
- `src/ppg_stroke/features/pyppg_extractor.py`: isolated PyPPG extraction wrapper for beat-level morphology tables.
- `src/ppg_stroke/features/preprocessing.py`: Step45-compatible Yeo-Johnson transform, REL residualization and time-only channels.
- `src/ppg_stroke/models/resnet1d.py`: 1D residual network used for PPG morphology sequences.
- `src/ppg_stroke/models/train_eval.py`: internal training, threshold selection and binary metrics.
- `src/ppg_stroke/models/aggregation.py`: prognosis sliding-window inference and patient/stay-level aggregation.
- `src/ppg_stroke/baselines/ehr.py`: structured EHR baselines with leakage-aware feature selection.
- `src/ppg_stroke/falsification/frozen_inference.py`: frozen-model pseudo-anchor and permutation-anchor diagnostic falsification.
- `src/ppg_stroke/reporting/extended_data_fig.py`: publication figure rendering for diagnostic falsification analyses.

## Command-line entry points

- `scripts/rebuild_warning_windows.py`: rebuild warning labels from recognition-anchor timing.
- `scripts/extract_ppg_features.py`: extract PyPPG beat-level morphology features from signal manifests.
- `scripts/train_warning_resnet.py`: train an internal MIMIC warning ResNet from prepared `.npz` tensors.
- `scripts/run_prognosis_external.py`: apply a frozen prognosis model to external sequence manifests.
- `scripts/run_ehr_baseline.py`: run internal cross-validation and frozen external EHR baselines.
- `scripts/run_falsification_inference.py`: run frozen pseudo-anchor and permutation-anchor analyses.
- `scripts/make_extended_data_figure.py`: regenerate the Extended Data falsification figure.

## Main documentation

- [`docs/METHODS_OVERVIEW.md`](docs/METHODS_OVERVIEW.md): manuscript-aligned workflow and modelling overview.
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md): reproduction levels, required inputs, and execution order.
- [`docs/DATA_ACCESS.md`](docs/DATA_ACCESS.md): data access, privacy, and source-dataset restrictions.
- [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md): intended use, training/validation design, risks, and limitations.
- [`docs/SOURCE_CODE_PROVENANCE.md`](docs/SOURCE_CODE_PROVENANCE.md): mapping from cleaned release modules to the real project scripts.
- [`docs/NEGATIVE_CONTROLS.md`](docs/NEGATIVE_CONTROLS.md): diagnostic falsification analyses and interpretation boundaries.
- [`docs/PPG_FEATURES.md`](docs/PPG_FEATURES.md): PPG morphology feature families and documentation requirements.
- [`docs/RESULTS_REPORTING.md`](docs/RESULTS_REPORTING.md): reporting conventions for metrics, validation, and figures.
- [`docs/MANUSCRIPT_ALIGNMENT.md`](docs/MANUSCRIPT_ALIGNMENT.md): claim map and wording constraints.

## Data availability

MIMIC-III and MC-MED are available through PhysioNet under the applicable access and data-use requirements. Raw waveforms, clinical notes, patient identifiers, source timestamps, and restricted derived files must not be committed to this repository. Derived analysis files may be shared only when permitted by the source-dataset terms and institutional policies.

## Quick start for authorized users

Full reproduction requires authorized access to the source datasets and project-specific derived anchor manifests. The code expects local paths to be supplied through a private copy of [`configs/study.example.yaml`](configs/study.example.yaml).

```bash
conda env create -f environment.yml
conda activate ppg-stroke-warning-prognosis
pip install -e .[dev,ehr,ppg]
pytest
```

Representative commands:

```bash
python scripts/rebuild_warning_windows.py \
  --input-csv features.csv \
  --output-csv windows_4h.csv \
  --horizon-min 240 \
  --stable-lookback-min 480 \
  --transition-buffer-min 15 \
  --blind-zone-min 15
python scripts/extract_ppg_features.py --manifest-csv waveform_manifest.csv --output-dir results/features
python scripts/train_warning_resnet.py --config configs/study.local.yaml
python scripts/run_prognosis_external.py --config configs/study.local.yaml
python scripts/run_falsification_inference.py --config configs/study.local.yaml
python scripts/make_extended_data_figure.py --plot-data-csv plot_data.csv --out-base results/extended_data_fig_1
```

After authorized inputs are available, the recommended order is:

1. Prepare local data paths outside the Git repository.
2. Build cohort and anchor manifests.
3. Extract PPG morphology features with the validated PyPPG-based pipeline.
4. Construct warning labels using the nominal horizon, the 15-min-per-side transition buffer and the separate 15-min recognition-proximal blind zone.
5. Train internal MIMIC-III models using patient-level or group-aware cross-validation.
6. Freeze preprocessing, thresholds, and model checkpoints.
7. Apply frozen models to MC-MED without retuning or recalibration.
8. Regenerate tables, figures, SHAP summaries, signal-quality analyses, and diagnostic falsification analyses.

Detailed instructions and required safeguards are in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Interpretation boundary

High warning probabilities in alternative pseudo-anchor or permutation-anchor analyses do **not** support a stroke-specific interpretation. They indicate that the warning output may capture a broader pre-recognition haemodynamic activation pattern enriched around clinically documented stroke recognition but not unique to stroke. Avoid describing the model as a stroke-specific diagnostic alert.

## License

No open-source license has been selected for this repository. Until an institutionally approved license is added, all rights are reserved. See `LICENSE_PENDING.md` for details.

## Citation

Cite the manuscript and the repository metadata in [`CITATION.cff`](CITATION.cff). Update DOI or URL fields after formal release.
