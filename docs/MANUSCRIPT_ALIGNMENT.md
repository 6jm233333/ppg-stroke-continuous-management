# Manuscript alignment and claim control

This document keeps repository wording aligned with the manuscript and prevents overclaiming.

## Manuscript title

Photoplethysmographic haemodynamic information for continuous stroke management

## Core claim

Routine PPG waveform morphology contains haemodynamic information relevant to two stages of stroke management:

1. Warning before clinically documented stroke recognition.
2. Prognosis stratification after stroke-associated hospitalization.

The claim is about additional continuous physiological information, not standalone diagnosis.

## Approved wording

Use these phrases consistently:

- routine PPG waveform morphology
- continuous haemodynamic information
- pre-recognition warning state
- clinically anchored stroke-recognition time
- nominal 4-, 5- and 6-h look-ahead horizons
- 15-min-per-side horizon-boundary transition buffer
- separate 15-min recognition-proximal blind zone
- frozen external validation
- patient-level split
- post-admission prognosis stratification
- improved versus worsened-or-deceased outcome
- non-specific pre-recognition haemodynamic activation
- continuous physiological warning layer

## Phrases to avoid

Avoid these phrases unless a future validated analysis truly supports them:

- stroke-specific warning
- stroke-specific diagnostic alert
- confirmed specificity
- negative controls confirmed robustness
- PPG diagnoses impending stroke
- event controls validated the model
- pseudo-anchor analysis confirmed specificity
- model replaces neurological assessment
- exact 4-, 5- or 6-h lead time
- positive warning window extending to the recognition anchor
- blind-zone sensitivity analysis when referring to recognition-anchor perturbation

## Diagnostic falsification interpretation

The correct interpretation is:

> Diagnostic falsification analyses show that warning probabilities were not restricted to clinically anchored stroke-recognition windows. This supports cautious interpretation: the warning signal is better described as a non-specific pre-recognition haemodynamic activation pattern that may be enriched before clinically documented stroke recognition.

## Windowing terminology

The warning-window protocol contains two separate exclusions:

1. A 15-min transition buffer on each side of the nominal horizon boundary.
2. A 15-min recognition-proximal blind zone covering \([-15,0)\) min.

Recognition-anchor perturbation, pseudo-anchor analysis and permutation-anchor analysis are separate sensitivity or falsification procedures and must not be described as blind-zone experiments.

## Clinical boundary

The repository should consistently state that the model may complement, but does not replace:

- neurological examination,
- neuroimaging,
- electrocardiography,
- laboratory testing,
- clinical scoring,
- structured clinical evaluation.

## Required consistency checks

Before release, search the repository for:

```text
stroke-specific
diagnostic alert
confirmed specificity
confirmed robustness
robust negative controls
blind_zone_min: 0
blind_zone_min: int = 0
up to the recognition anchor
no separate pre-anchor blind zone
```

Any occurrence must be justified as a phrase-to-avoid example or removed.
