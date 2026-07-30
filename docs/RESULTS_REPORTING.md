# Results reporting standards

## Primary metric

F1 score is the primary performance metric for the manuscript. Accuracy, precision, and recall are secondary metrics.

## Required context for every metric

Every reported metric should specify:

- Task: warning or prognosis.
- Dataset: MIMIC-III or MC-MED.
- Validation mode: internal cross-validation or frozen external validation.
- Nominal look-ahead horizon for warning results.
- The 15-min-per-side horizon-boundary transition buffer.
- The separate 15-min recognition-proximal blind zone.
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
- "nominal 4-, 5- or 6-h look-ahead scheme"
- "the final 15 min before documented recognition were excluded"

Avoid:

- "stroke-specific diagnostic alert"
- "confirmed specificity"
- "diagnoses impending stroke"
- "robust negative controls confirmed the model"
- "prediction exactly 4, 5 or 6 h before recognition"
- treating recognition-anchor perturbation as a blind-zone analysis

## Tables

Publication-ready tables should:

- Use patient-level or hospitalization-level denominators where possible.
- Include window counts only as secondary context.
- State whether summaries are mean +/- s.d., median (IQR), or bootstrap confidence intervals.
- Separate reference analyses from diagnostic falsification analyses.
- Move interpretation caveats to table notes instead of repeating them in every row.
- State the nominal horizon, transition buffer and recognition-proximal blind zone when reporting warning results.

## Figures

Figures should:

- Avoid explanatory text blocks inside data panels.
- Use consistent colors for anchor groups and tasks.
- Put interpretive caveats in captions or main text.
- Show uncertainty and denominators when possible.
- Preserve a clear distinction between primary results and diagnostic falsification analyses.

## Negative-control reporting

Pseudo-anchor and permutation-anchor results should be reported as diagnostic falsification analyses. High probabilities in these analyses temper interpretation; they do not support model specificity.

Event-specific controls should be reported only when validated event-anchor timing exists. Recognition-anchor perturbation should be described as timestamp-uncertainty sensitivity analysis, not as a blind-zone experiment.
