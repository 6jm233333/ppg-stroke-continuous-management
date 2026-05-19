from __future__ import annotations

import pandas as pd
import pytest

from ppg_stroke.schemas import RAW_PPG_FEATURES, require_columns


def test_raw_feature_schema_has_expected_length():
    assert len(RAW_PPG_FEATURES) == 17
    assert len(set(RAW_PPG_FEATURES)) == 17


def test_require_columns_reports_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        require_columns(pd.DataFrame({"a": [1]}), ["a", "b"], context="demo")
