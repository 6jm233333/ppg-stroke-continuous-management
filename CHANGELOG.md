# Changelog

## Unreleased

### Fixed

- Corrected the released warning-window default from `blind_zone_min=0` to `blind_zone_min=15` to match the authoritative analysis protocol.
- Updated configuration, command-line defaults, unit tests and documentation to exclude the final 15 min before documented stroke recognition.
- Clarified that the 15-min recognition-proximal blind zone is separate from the 15-min-per-side horizon-boundary transition buffer and from recognition-anchor perturbation analyses.
- No reported performance values were recalculated or changed.

## 0.1.0 - 2026-05-19

- Added manuscript-aligned GitHub project files.
- Added reusable source modules for warning-window construction, PPG feature preprocessing, ResNet-1D training, prognosis aggregation, EHR baselines, frozen falsification inference and figure rendering.
- Added command-line workflow entry points and example configuration.
- Added conservative interpretation guidance for pre-recognition warning and diagnostic falsification analyses.
- Added data-access, reproducibility, model-card, reporting, and release-checklist documentation.
- Added source-code provenance mapping from release modules to the working analysis scripts.
