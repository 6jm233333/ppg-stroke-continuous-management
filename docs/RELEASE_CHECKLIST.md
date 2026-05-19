# Release checklist

Use this checklist before making the repository public or archiving it with a DOI.

## Manuscript alignment

- [ ] Repository title matches the manuscript title.
- [ ] README describes both tasks: warning and prognosis.
- [ ] Warning output is not described as stroke-specific.
- [ ] Diagnostic falsification analyses are described as cautionary evidence, not specificity evidence.
- [ ] Data availability and code availability statements match the manuscript or approved public-release language.

## Data governance

- [ ] No raw clinical data are committed.
- [ ] No waveform files are committed.
- [ ] No clinical notes or note snippets are committed.
- [ ] No patient identifiers or restricted timestamps are committed.
- [ ] No unauthorized checkpoints, feature matrices, or derived patient-level files are committed.
- [ ] Source-dataset terms permit all files included in the release.

## Reproducibility

- [ ] Source code is present in `src/` and scripts are present in `scripts/`.
- [ ] Configuration files are documented and contain no private paths.
- [ ] Environment is pinned.
- [ ] Random seeds and deterministic settings are documented.
- [ ] Patient-level and group-aware splits are tested.
- [ ] MC-MED frozen external validation guardrails are tested.
- [ ] Tables and figures can be regenerated from scripts.

## Software quality

- [ ] Tests pass.
- [ ] Scripts fail clearly when restricted inputs are missing.
- [ ] Logs do not print sensitive identifiers.
- [ ] Notebook outputs are cleared or moved to reproducible scripts.
- [ ] README quick start has been tested on a clean machine or environment.

## Publication metadata

- [ ] `CITATION.cff` has final repository URL.
- [ ] DOI or Zenodo metadata are added if available.
- [ ] License is approved and replaces `LICENSE_PENDING.md`.
- [ ] Version tag is created.
- [ ] Changelog is updated.