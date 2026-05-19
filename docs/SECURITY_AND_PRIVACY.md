# Security and privacy

## Principle

This project uses restricted retrospective clinical and waveform datasets. The repository must be safe to publish without exposing protected health information, restricted identifiers, source timestamps, or data-use-restricted derived artifacts.

## Never commit

- Raw clinical data.
- Raw waveform files.
- Clinical notes.
- Patient identifiers.
- Admission identifiers when not approved for sharing.
- Exact source event timestamps.
- Credentials, tokens, keys, database connection strings, or private URLs.
- Trained weights or feature matrices unless explicitly approved for release.

## Required pre-release scans

Before public release, run scans for:

- file names containing patient or admission identifiers,
- absolute local paths,
- PHI-like strings,
- clinical note snippets,
- large binary waveform files,
- checkpoint and feature-matrix files,
- secrets or environment files.

## Recommended Git hygiene

- Keep restricted data outside the repository root.
- Use `.gitignore` for data, model, output, and cache directories.
- Review `git status --ignored` before release.
- If restricted data was ever committed, do not simply delete it in a later commit; rewrite history under institutional guidance before publication.

## Public release rule

A release is not ready until a person with dataset governance responsibility confirms that all committed files are safe for public sharing.