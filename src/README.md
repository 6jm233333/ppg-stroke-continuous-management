# Source modules

Reusable implementation code lives here:

- `ppg_stroke/features/`: PPG morphology extraction wrappers, Step6 warning labels and Step45 feature preprocessing.
- `ppg_stroke/models/`: ResNet-1D, training utilities, tensor datasets and prognosis aggregation.
- `ppg_stroke/baselines/`: structured EHR baseline models.
- `ppg_stroke/falsification/`: frozen-model pseudo-anchor and permutation-anchor analyses.
- `ppg_stroke/reporting/`: publication figure generation.
- `ppg_stroke/schemas.py`: canonical PPG feature lists and schema checks.

Do not place notebooks, local paths, or restricted data in this directory.
