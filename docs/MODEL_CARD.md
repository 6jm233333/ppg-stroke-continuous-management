# Model card

## Model family

The primary PPG model is a one-dimensional residual neural network (ResNet-1D) that operates on ordered beat-level PPG morphology features. Structured EHR baselines use tree-based ensemble models such as LightGBM, XGBoost, and Random Forest.

## Intended scientific use

The models are intended for retrospective evaluation of whether routine PPG waveform morphology contains continuous haemodynamic information relevant to:

- Warning before clinically documented in-hospital stroke recognition.
- Prognosis stratification after stroke-associated hospitalization.

They are research models, not deployed clinical decision systems.

## Non-use cases

The models must not be used as:

- A stroke-specific diagnostic alert.
- A replacement for neurological assessment.
- A replacement for neuroimaging, ECG, laboratory testing, or structured clinical evaluation.
- A treatment-triggering device.
- A prospective clinical surveillance system without independent validation and governance.

## Training and validation design

- Internal development: MIMIC-III.
- External validation: MC-MED.
- Warning split: patient-level stratified five-fold cross-validation in MIMIC-III.
- Warning-window protocol: a 15-min transition buffer on each side of the nominal horizon boundary and a separate 15-min recognition-proximal blind zone.
- Warning exclusion: PPG observations in the final 15 min before documented recognition are excluded from training and evaluation.
- Prognosis split: stratified group-aware five-fold cross-validation in MIMIC-III.
- External validation rule: frozen preprocessing, frozen model checkpoints, and no retuning or recalibration on MC-MED.

## Inputs

The PPG model input is a temporal sequence of morphology features extracted from PPG waveforms. The structured EHR baselines use demographics, comorbidities, laboratory measurements, and summarized vital signs available before the relevant prediction time.

Signal-quality and retention analyses are used to assess feasibility. They should not silently become prediction features.

## Outputs

The model outputs class probabilities. Threshold-dependent metrics are reported for predefined or validation-selected thresholds. External validation thresholds must be frozen before MC-MED evaluation.

## Known risks

- Time-to-anchor confounding in the warning task.
- Non-specific haemodynamic activation shared across alternative anchor windows.
- Dataset shift between MIMIC-III and MC-MED.
- Differential performance across demographic or clinical subgroups.
- Sensitivity to waveform availability, monitoring practice, and signal quality.
- Retrospective label uncertainty from clinical documentation.

## Required reporting

Every model result should report:

- Dataset and task.
- Nominal look-ahead horizon or prognosis label definition.
- Warning-window transition buffer and recognition-proximal blind zone.
- Split design.
- Number of patients or hospitalizations.
- Number of windows or waveform units when applicable.
- Primary and secondary metrics.
- Threshold-selection rule.
- Whether the result is internal development, cross-validation, or frozen external validation.

## Interpretation statement

The pre-recognition warning model should be described as detecting a pre-recognition haemodynamic warning signal or physiological activation pattern. It should not be described as confirming stroke specificity.
