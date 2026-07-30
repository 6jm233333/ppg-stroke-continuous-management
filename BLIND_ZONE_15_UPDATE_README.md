# Blind-zone correction overlay

This overlay corrects the public repository so that the warning-window protocol uses:

- `stable_lookback_min = 480`
- `transition_buffer_min = 15`
- `blind_zone_min = 15`

For a nominal horizon H, the default label intervals are:

- negative: `[-480, -(H + 15)]`
- transition exclusion: `(-(H + 15), -(H - 15))`
- positive: `[-(H - 15), -15)`
- recognition-proximal blind zone: `[-15, 0)`
- at/after recognition: excluded

Copy the files over the same paths in the repository. No model results are included or changed.
