from __future__ import annotations

import numpy as np

from ppg_stroke.models.aggregation import aggregate_window_probabilities, max_consecutive_true


def test_max_and_mean_aggregation():
    probs = np.asarray([0.1, 0.4, 0.7])
    assert aggregate_window_probabilities(probs, method="max", threshold=0.5) == (0.7, 1)
    score, pred = aggregate_window_probabilities(probs, method="mean", threshold=0.5)
    assert np.isclose(score, 0.4)
    assert pred == 0


def test_consecutive_aggregation():
    probs = np.asarray([0.7, 0.8, 0.2, 0.9])
    score, pred = aggregate_window_probabilities(probs, method="consecutive_k2", threshold=0.5)
    assert score == 1.0
    assert pred == 1
    assert max_consecutive_true([True, False, True, True]) == 2
