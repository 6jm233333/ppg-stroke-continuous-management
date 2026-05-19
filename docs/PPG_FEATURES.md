# PPG morphology features

## Overview

The manuscript uses a fixed 17-feature beat-level PPG morphology representation derived from the raw PPG waveform, the velocity plethysmogram, and the acceleration plethysmogram. These features capture complementary aspects of pulse morphology.

## Feature families

The retained representation spans:

- Systolic timing.
- Pulse amplitude.
- Pulse interval and beat-to-beat timing variability.
- Derivative-domain fiducial timing from VPG and APG waveforms.
- Normalized systolic-diastolic timing structure.
- Pulse-shape stability and morphology variability.
- Baseline and offset amplitude structure.

## Manuscript-aligned operational definitions

The feature set includes descriptors with the following operational meanings:

| Family | Example operational definition | Physiological rationale |
|---|---|---|
| Systolic timing | Time from pulse onset to systolic peak | Systolic upstroke timing and pulse-wave transmission |
| Upstroke steepness | Ratio of pulse amplitude to systolic time | Stiffness-related systolic morphology |
| Rhythm variability | Coefficient of variation of pulse interval | Beat-to-beat rhythm variability |
| Offset morphology | PPG amplitude at pulse offset | End-cycle waveform recovery |
| Peak amplitude | PPG amplitude at systolic peak | Systolic pulse magnitude and peripheral perfusion |
| Cycle balance | Ratio of systolic to diastolic duration | Cardiac-cycle timing balance |
| VPG timing | Time from pulse onset to VPG fiducial points | Velocity-domain systolic and post-systolic timing |
| APG timing | Time from pulse onset to APG fiducial points | Acceleration and wave-reflection-related timing |
| Amplitude variability | Coefficient of variation of pulse amplitude | Beat-to-beat perfusion variability |
| Pulse interval | Time between consecutive pulse onsets | Pulse-cycle duration |

## Baseline-relative warning features

For the warning task, selected morphology features are transformed relative to a subject-specific stable baseline. These baseline-relative variables are transformations of the core morphology features and should be tracked separately from the base feature dictionary.

## Documentation requirements before code release

The implementation should include a machine-readable feature dictionary with:

- Feature name used in code.
- Operational definition.
- Units or dimensionless status.
- Fiducial points required.
- Whether the feature is timing, amplitude, normalized timing, derivative-domain, or variability based.
- Whether a baseline-relative transformation is used in the warning task.
- Missingness and quality-control rules.
- Mapping to manuscript terminology.

Do not rely on implicit column order alone.