# Results reporting standards

## Primary metric

F1 score is the primary performance metric for the manuscript. Accuracy, precision, and recall are secondary metrics.

## Required context for every metric

Every reported metric should specify:

- Task: warning or prognosis.
- Dataset: MIMIC-III or MC-MED.
- Validation mode: internal cross-validation or frozen external validation.
- Prediction horizon for warning results.
- Outcome definition for prognosis results.
- Patient, hospitalization, or window count.
- Threshold-selection rule.
- Mean and uncertainty summary.

## External validation wording

Use:

- "frozen external validation"
- "applied without retuning or recalibration"
- "thresholds were not optimized on MC-MED"

Avoid:

- "trained and tested on MC-MED"
- "externally optimized"
- "externally tuned"
- any wording implying MC-MED influenced model selection

## Warning interpretation wording

Use:

- "pre-recognition haemodynamic warning signal"
- "continuous physiological activation"
- "warning probability"
- "clinically anchored stroke-recognition windows"

Avoid:

- "stroke-specific diagnostic alert"
- "confirmed specificity"
- "diagnoses impending stroke"
- "robust negative controls confirmed the model"

## Tables

Publication-ready tables should:

- Use patient-level or hospitalization-level denominators where possible.
- Include window counts only as secondary context.
- State whether summaries are mean +/- s.d., median (IQR), or bootstrap confidence intervals.
- Separate reference analyses from diagnostic falsification analyses.
- Move interpretation caveats to table notes instead of repeating them in every row.

## Figures

Figures should:

- Avoid explanatory text blocks inside data panels.
- Use consistent colors for anchor groups and tasks.
- Put interpretive caveats in captions or main text.
- Show uncertainty and denominators when possible.
- Preserve a clear distinction between primary results and diagnostic falsification analyses.

## Negative-control reporting

Pseudo-anchor and permutation-anchor results should be reported as diagnostic falsification analyses. High probabilities in these analyses temper interpretation; they do not support model specificity.

Event-specific controls should be reported only when validated event-anchor timing exists.