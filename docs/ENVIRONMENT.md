# Environment management

## Recommended baseline

Use an isolated Python environment. The exact package versions should be pinned after the implementation is added and validated.

A typical stack includes:

- Python 3.10 or later.
- PyTorch for ResNet-1D models.
- NumPy, pandas, SciPy, and scikit-learn.
- LightGBM, XGBoost, and Random Forest baselines.
- PyPPG or the validated local PPG morphology extraction package.
- SHAP for interpretation.
- matplotlib and seaborn for figures.
- pytest for tests.

## Reproducibility requirement

Before public release, create one of the following:

- `environment.yml` with exact conda package versions, or
- `requirements.txt` plus a Python version file, or
- a container definition such as `Dockerfile` or `environment.lock.yml`.

The environment specification should include CPU/GPU assumptions and deterministic settings where applicable.

## Local path management

Private paths should be set through environment variables or ignored local config files. Do not commit absolute paths such as local drive letters or institutional mount points.

## Suggested environment variables

```text
PPG_STROKE_DATA_ROOT=<secure local data root>
PPG_STROKE_OUTPUT_ROOT=<secure local output root>
PPG_STROKE_CONFIG=<path to local config>
```

## Version logging

Every run should export a machine-readable run manifest containing:

- Python version.
- Package versions.
- Git commit hash.
- Configuration hash.
- Data manifest hash.
- Random seeds.
- Output directory.