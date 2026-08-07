import csv

import pytest

from research.smile_metric_robustness import (
    METRICS,
    RobustnessConfig,
    run_robustness_research,
)


def _records(path):
    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


def test_zero_noise_pipeline_recovers_quadratic_truth(tmp_path) -> None:
    config = RobustnessConfig(
        repetitions=1,
        price_noise_stds=(0.0,),
        strike_densities=(33,),
    )
    outputs = run_robustness_research(tmp_path, config)
    record = _records(outputs.experiment_records_path)[0]

    assert int(record["selected_point_count"]) == 33
    assert float(record["atm_error"]) == pytest.approx(0.0, abs=1e-8)
    assert float(record["skew_error"]) == pytest.approx(0.0, abs=1e-7)
    assert float(record["curvature_error"]) == pytest.approx(0.0, abs=1e-6)
    assert float(record["rr25_error"]) == pytest.approx(0.0, abs=3e-4)
    assert float(record["bf25_error"]) == pytest.approx(0.0, abs=3e-4)


def test_outputs_are_deterministic_and_summary_is_complete(tmp_path) -> None:
    config = RobustnessConfig(
        repetitions=2,
        base_seed=17,
        price_noise_stds=(0.0, 0.01),
        strike_densities=(9, 17),
    )
    first = run_robustness_research(tmp_path / "first", config)
    second = run_robustness_research(tmp_path / "second", config)

    assert first.experiment_count == 8
    assert first.experiment_records_path.read_bytes() == (
        second.experiment_records_path.read_bytes()
    )
    assert first.quote_records_path.read_bytes() == second.quote_records_path.read_bytes()
    assert first.summary_path.read_bytes() == second.summary_path.read_bytes()
    summary = _records(first.summary_path)
    assert len(summary) == 2 * 2 * len(METRICS)
    assert {row["metric"] for row in summary} == set(METRICS)
    assert all(int(row["experiment_count"]) == 2 for row in summary)
    assert all(row["selected_point_count_mean"] for row in summary)


@pytest.mark.parametrize("density", [2, 4, 8])
def test_strike_density_requires_odd_point_count(density) -> None:
    with pytest.raises(ValueError, match="odd integers"):
        RobustnessConfig(strike_densities=(density,))
