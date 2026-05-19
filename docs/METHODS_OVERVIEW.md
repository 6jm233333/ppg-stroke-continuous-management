# Methods overview

## Study objective

The project evaluates whether routine PPG waveform morphology provides continuous haemodynamic information for stroke management. The study has two related but clinically distinct tasks:

1. **Pre-recognition warning**: identify a warning state before clinically documented in-hospital stroke recognition.
2. **Post-admission prognosis stratification**: distinguish improved from worsened-or-deceased clinical trajectories after stroke-associated hospitalization.

MIMIC-III is used for internal development. MC-MED is reserved for frozen external validation.

## Data sources

The manuscript uses de-identified retrospective clinical and waveform datasets. Data access is governed by source-dataset requirements. No prospective recruitment, intervention, or bedside deployment is part of the study.

## Cohort construction

### Pre-recognition warning cohort

Eligible records are monitored inpatients who had not yet developed stroke during the analysed pre-event period but subsequently had clinically documented in-hospital stroke recognition. PPG segments are aligned to the clinical stroke-recognition anchor. Warning horizons are evaluated at 4, 5 and 6 h before the anchor.

### Prognosis cohort

Eligible records are stroke-associated hospitalizations with waveform linkage and trajectory labels. The primary binary prognosis task contrasts improved versus worsened-or-deceased outcomes. Stable courses are excluded from this binary experiment.

## Temporal anchors and leakage prevention

The warning task depends on clinically anchored stroke-recognition times derived from clinical documentation. The temporal design must preserve:

- A stable baseline interval for subject-specific normalization.
- A transition buffer between stable and warning windows.
- A lead-time blind zone near the recognition anchor to reduce leakage from peri-recognition physiology.
- Patient-level split integrity so that windows from the same patient do not cross train/test boundaries.

## PPG morphology extraction

Waveforms are temporally aligned to the relevant clinical timeline and processed with a PyPPG-based morphology pipeline. The feature representation uses 17 beat-level morphology descriptors spanning timing, amplitude, derivative-domain timing, normalized structure, and beat-to-beat variability.

For the warning task, selected features are transformed to baseline-relative variables using subject-specific stable baseline values. These are transformations of core morphology features, not additional independent feature families.

## Models

### PPG morphology model

Both tasks use a one-dimensional residual neural network (ResNet-1D) implemented in PyTorch to model temporal dependencies in beat-level PPG morphology streams.

- Warning: trained on MIMIC-III with patient-level stratified five-fold cross-validation; frozen for MC-MED external validation.
- Prognosis: trained with group-aware cross-validation in MIMIC-III; evaluated externally on MC-MED using frozen preprocessing and decision rules.

### Structured EHR baselines

Structured EHR baselines include tree-based learners such as LightGBM, XGBoost, and Random Forest. These baselines explicitly exclude PPG waveform morphology, free-text features, imaging sequences, and downstream treatment trajectories. Variables are restricted to information available before the corresponding prediction horizon or baseline time point.

## Validation design

Internal development uses MIMIC-III. External validation uses MC-MED without retuning, recalibration, or threshold optimization. F1 score is the primary performance metric; accuracy, precision, and recall are secondary metrics.

## Interpretation

The models are intended to evaluate whether PPG morphology contains continuous haemodynamic information relevant to stroke-care workflows. They are not diagnostic replacements for standard clinical assessment. In particular, the pre-recognition warning output should not be described as stroke-specific.