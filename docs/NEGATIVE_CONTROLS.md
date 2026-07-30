# Diagnostic falsification and negative-control analyses

## Purpose

Diagnostic falsification analyses assess whether high frozen-model warning probabilities are restricted to clinically anchored stroke-recognition windows or also appear around alternative temporal anchors.

These analyses are designed to stress-test interpretation. They are not used for model training, model selection, recalibration, or threshold optimization.

## Distinction from the recognition-proximal blind zone

The fixed 15-min recognition-proximal blind zone is part of the primary warning-label construction and excludes samples in \([-15,0)\) min before documented recognition.

Recognition-anchor perturbation is a separate timestamp-uncertainty analysis in which the documented recognition anchor is shifted and labels are regenerated under the same windowing protocol.

Pseudo-anchor and permutation-anchor analyses are diagnostic falsification analyses. None of these analyses should be described as a blind-zone experiment.

## Included paper-ready analyses

### Pseudo-anchor analysis

Alternative anchors are sampled within stroke hospitalizations when usable pre-anchor PPG feature windows are available. These anchors are diagnostic alternatives and should be interpreted cautiously, especially when they occur after documented stroke recognition.

### Permutation-anchor analysis

Anchor timing is reassigned across patients to retain admission-relative temporal structure while disrupting the original patient-anchor pairing.

### Frozen-model rule

Both analyses must use the frozen PPG warning model without:

- retraining,
- recalibration,
- threshold optimization,
- feature re-selection,
- MC-MED-informed tuning.

## Excluded analysis: event-specific controls

Event-specific controls should not be included unless validated event-anchor timing is available for the non-stroke clinical event. Diagnosis summaries or cohort summaries are not sufficient to define minute-level anchors for hypotension, shock, intubation, mechanical ventilation, sepsis, or suspected infection.

If validated event-anchor timing is insufficient, event-specific controls should be documented as not retained rather than forced into a figure or table.

## Interpretation

High probabilities in pseudo-anchor or permutation-anchor windows do not confirm robustness or stroke specificity. They indicate that the warning output may capture broader physiological activation, monitoring context, or temporal structure that is not unique to clinically documented stroke recognition.

Preferred wording:

> Diagnostic falsification analyses showed that frozen-model warning probabilities were not restricted to clinically anchored stroke-recognition windows. Elevated probabilities in alternative pseudo-anchor and permutation-anchor windows indicate that the warning output should be interpreted as a non-specific pre-recognition haemodynamic activation signal rather than a stroke-specific diagnostic alert.

Avoid:

- "negative controls confirmed specificity"
- "pseudo-anchor analysis confirmed robustness"
- "stroke-specific warning"
- "diagnostic alert"
- "event controls validated the model" unless validated event anchors actually exist
- "blind-zone analysis" when referring to anchor perturbation, pseudo-anchor or permutation-anchor analyses
