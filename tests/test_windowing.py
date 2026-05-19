from __future__ import annotations

import pandas as pd

from ppg_stroke.features.windowing import apply_warning_labels, assign_warning_label


def test_assign_warning_label_excludes_ambiguous_regions():
    assert assign_warning_label(-500, horizon_min=240) == -1
    assert assign_warning_label(-300, horizon_min=240) == 0
    assert assign_warning_label(-240, horizon_min=240) == -1
    assert assign_warning_label(-220, horizon_min=240) == 1
    assert assign_warning_label(-10, horizon_min=240) == 1
    assert assign_warning_label(5, horizon_min=240) == -1


def test_apply_warning_labels_vectorized():
    df = pd.DataFrame({"Time_Rel_Min": [-300, -240, -220]})
    out = apply_warning_labels(df, horizon_min=240)
    assert out["Label"].tolist() == [0, -1, 1]
