from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


RAW_PPG_FEATURES = [
    "T_sp_Rel",
    "T_sp",
    "SI",
    "CV_T_pi",
    "A_off",
    "A_sp_Rel",
    "SI_Rel",
    "Tsys_Tdia",
    "Tu_Tpi",
    "Tb_Tpi",
    "CV_Pulse_Amplitude",
    "T_v",
    "Tu_Ta_Tpi",
    "DSI_Rel",
    "T_c_Rel",
    "A_off_Rel",
    "A_on_Rel",
]

RELATIVE_FEATURES = [
    "T_sp_Rel",
    "A_sp_Rel",
    "SI_Rel",
    "DSI_Rel",
    "T_c_Rel",
    "A_off_Rel",
    "A_on_Rel",
]

NOREL_FEATURES = [f for f in RAW_PPG_FEATURES if f not in RELATIVE_FEATURES]

WARNING_REQUIRED_COLUMNS = [
    "Group_ID",
    "Source_File",
    "Beat_Idx",
    "Label",
    "Absolute_Time",
    "Time_Rel_Min",
]

PROGNOSIS_REQUIRED_COLUMNS = [
    "Dataset",
    "Subject_ID",
    "Group_ID",
    "Trend_Label",
    "Label_Code",
]


@dataclass(frozen=True)
class FeatureSet:
    name: str
    columns: list[str]


FEATURE_SETS = {
    "raw": FeatureSet("raw", RAW_PPG_FEATURES),
    "relative": FeatureSet("relative", RELATIVE_FEATURES),
    "no_relative": FeatureSet("no_relative", NOREL_FEATURES),
    "time_only": FeatureSet("time_only", ["Time_Rel_Min"]),
}


def require_columns(df: pd.DataFrame, columns: Iterable[str], context: str = "dataframe") -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{context} missing required columns: {missing}")


def numeric_feature_frame(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    require_columns(df, columns, context="feature frame")
    out = df[list(columns)].apply(pd.to_numeric, errors="coerce")
    return out.replace([float("inf"), float("-inf")], pd.NA)
