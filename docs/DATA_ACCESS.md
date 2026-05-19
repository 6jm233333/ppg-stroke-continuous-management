# Data access and governance

## Source datasets

The manuscript analyses MIMIC-III and MC-MED. These datasets are available through PhysioNet under applicable credentialing, training, access, and data-use requirements.

This repository must not contain raw or restricted source data.

## Files that must not be committed

Do not commit:

- Raw waveform files.
- Clinical notes or note-derived raw text.
- Patient identifiers, admission identifiers, or source row identifiers unless fully approved for sharing.
- Exact source timestamps that could re-identify clinical events.
- Restricted derived feature matrices.
- Model checkpoints trained on restricted data unless sharing is explicitly approved.
- Any file containing local access paths, credentials, tokens, or database connection strings.

## Expected local data layout

Authorized users should store data outside the repository. A typical local layout is:

```text
<secure_data_root>/
  mimiciii/
    raw/
    waveform/
    derived/
  mcmed/
    raw/
    waveform/
    derived/
  manifests/
    warning_anchor_manifest.csv
    prognosis_label_manifest.csv
    waveform_linkage_manifest.csv
  outputs/
    features/
    checkpoints/
    figures/
    tables/
```

Paths should be referenced through configuration files or environment variables, never hard-coded in source code.

## Minimum manifest fields

A release-ready implementation should document the schema for each manifest. At minimum, anchor and linkage manifests should contain non-identifying surrogate keys and enough temporal information to reproduce window construction under approved data-use terms.

For event-specific controls, the required fields include:

- `event_type`
- `patient_uid`
- `hospitalization_id`
- `event_anchor_time`
- `event_definition_source`
- `has_stroke_same_stay`
- `stroke_anchor_time_if_any`
- `distance_to_stroke_anchor_hours`
- `feature_path`
- `model_checkpoint`

If validated event-anchor timing is unavailable, event-specific controls should not be presented as paper-ready results.

## Derived data sharing

Derived analysis files may be shared only when all of the following are true:

- Sharing is permitted by the source-dataset terms.
- The institutional review and data-use policies allow sharing.
- Identifiers, free-text snippets, and exact restricted timestamps have been removed or transformed as required.
- The file is necessary for reproducibility and cannot be replaced by a safer summary.

When in doubt, share code and synthetic schema examples rather than restricted derived data.