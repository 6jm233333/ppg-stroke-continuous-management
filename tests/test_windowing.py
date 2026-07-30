from __future__ import annotations

import pandas as pd

from ppg_stroke.features.windowing import apply_warning_labels, assign_warning_label


def test_assign_warning_label_excludes_ambiguous_regions():
    # Outside the 8-h look-back range.
    assert assign_warning_label(-500, horizon_min=240) == -1

    # Stable negative interval: [-480, -255].
    assert assign_warning_label(-480, horizon_min=240) == 0
    assert assign_warning_label(-300, horizon_min=240) == 0
    assert assign_warning_label(-255, horizon_min=240) == 0

    # Horizon-boundary transition interval: (-255, -225).
    assert assign_warning_label(-254, horizon_min=240) == -1
    assert assign_warning_label(-240, horizon_min=240) == -1
    assert assign_warning_label(-226, horizon_min=240) == -1

    # Positive warning interval: [-225, -15).
    assert assign_warning_label(-225, horizon_min=240) == 1
    assert assign_warning_label(-220, horizon_min=240) == 1
    assert assign_warning_label(-16, horizon_min=240) == 1

    # Recognition-proximal blind zone and post-anchor interval.
    assert assign_warning_label(-15, horizon_min=240) == -1
    assert assign_warning_label(-10, horizon_min=240) == -1
    assert assign_warning_label(-1, horizon_min=240) == -1
    assert assign_warning_label(0, horizon_min=240) == -1
    assert assign_warning_label(5, horizon_min=240) == -1


def test_apply_warning_labels_vectorized():
    df = pd.DataFrame(
        {
            "Time_Rel_Min": [
                -500,
                -300,
                -255,
                -240,
                -225,
                -220,
                -16,
                -15,
                -10,
                0,
            ]
        }
    )
    out = apply_warning_labels(df, horizon_min=240)
    assert out["Label"].tolist() == [-1, 0, 0, -1, 1, 1, 1, -1, -1, -1]


def test_blind_zone_is_shared_across_nominal_horizons():
    for horizon_min in (240, 300, 360):
        assert assign_warning_label(-16, horizon_min=horizon_min) == 1
        assert assign_warning_label(-15, horizon_min=horizon_min) == -1
        assert assign_warning_label(-10, horizon_min=horizon_min) == -1
