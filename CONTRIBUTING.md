# Contributing

This repository is intended for reproducible scientific code supporting a clinical waveform manuscript. Contributions should prioritize correctness, auditability, and protection of restricted clinical data.

## Ground rules

- Do not commit raw clinical data, waveform files, clinical notes, patient identifiers, source timestamps, or restricted derived files.
- Keep all dataset paths configurable and local.
- Preserve patient-level and hospitalization-level split boundaries.
- Do not tune thresholds, preprocessing, or model hyperparameters on MC-MED external validation data.
- Document any change that could affect reported metrics, anchor definitions, feature extraction, or leakage prevention.

## Pull request checklist

Before requesting review, confirm that:

- The change has a narrow scientific purpose.
- Unit tests or smoke tests were added when applicable.
- Generated outputs are reproducible from scripts and configuration files.
- No PHI, source notes, waveform excerpts, or restricted files are included.
- Documentation is updated if the workflow, assumptions, or outputs changed.
- Claims remain aligned with `docs/MANUSCRIPT_ALIGNMENT.md`.