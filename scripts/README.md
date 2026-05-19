# Scripts

Command-line scripts orchestrate reproducible workflow stages. They call reusable code from `src/ppg_stroke` and keep local paths in private config files.

Available entry points:

- `rebuild_warning_windows.py`: assign 4 h, 5 h or 6 h warning labels from recognition-anchor timing.
- `extract_ppg_features.py`: extract PyPPG beat-level morphology features from signal manifests.
- `train_warning_resnet.py`: train the internal PPG warning ResNet from prepared tensor arrays.
- `run_prognosis_external.py`: apply a frozen prognosis ResNet to external sequence manifests.
- `run_ehr_baseline.py`: run structured EHR baselines with internal CV and optional external validation.
- `run_falsification_inference.py`: run frozen pseudo-anchor and permutation-anchor diagnostic analyses.
- `make_extended_data_figure.py`: regenerate the falsification Extended Data figure.

Scripts fail safely if required restricted inputs are missing.
