from datetime import date
import math

import pandas as pd
import pytest

from ncx_derivatives.volatility import SmileIvSource
from research.real_data.common.dataset_audit import audit_standardized_options
from research.real_data.common.optionsdx_adapter import (
    optionsdx_stage2_csv_config,
    standardize_optionsdx_wide,
)
from research.real_data.research_001_atm_stability.build_tenor_panel import (
    add_daily_stability,
    build_nearest_tenor_panel,
)
from research.real_data.research_001_atm_stability.config import Research001Config
from research.real_data.research_001_atm_stability.historical_carry import (
    CashDividendScheduleCurve,
    InterpolatedZeroRateCurve,
    projected_dividend_schedule,
    trailing_dividend_cash,
)


def _wide_rows():
    return pd.DataFrame(
        [
            {
                "[QUOTE_DATE]": "2022-01-03",
                "[EXPIRE_DATE]": "2022-02-18",
                "[DTE]": 46,
                "[UNDERLYING_LAST]": 470.0,
                "[STRIKE]": 470.0,
                "[C_BID]": 10.0,
                "[C_ASK]": 11.0,
                "[P_BID]": 9.0,
                "[P_ASK]": 10.0,
                "[C_IV]": 0.20,
                "[P_IV]": 0.21,
            },
            {
                "[QUOTE_DATE]": "2022-01-03",
                "[EXPIRE_DATE]": "2022-02-18",
                "[DTE]": 46,
                "[UNDERLYING_LAST]": 470.0,
                "[STRIKE]": 475.0,
                "[C_BID]": 8.0,
                "[C_ASK]": 9.0,
                "[P_BID]": 11.0,
                "[P_ASK]": 12.0,
                "[C_IV]": 0.19,
                "[P_IV]": 0.22,
            },
        ]
    )


def test_optionsdx_adapter_expands_both_sides_and_is_order_invariant() -> None:
    original = standardize_optionsdx_wide(_wide_rows(), underlying_symbol="spy")
    reversed_rows = standardize_optionsdx_wide(
        _wide_rows().iloc[::-1].reset_index(drop=True), underlying_symbol="SPY"
    )

    assert len(original) == 4
    assert original["option_type"].value_counts().to_dict() == {"call": 2, "put": 2}
    comparable = [column for column in original.columns if column != "source_row"]
    pd.testing.assert_frame_equal(original[comparable], reversed_rows[comparable])
    assert original["valuation_timestamp"].map(lambda value: value.tzinfo is not None).all()
    assert optionsdx_stage2_csv_config(dataset_id="pilot").mapping.bid == "bid"


def test_audit_records_failures_without_dropping_rows() -> None:
    frame = standardize_optionsdx_wide(_wide_rows(), underlying_symbol="SPY")
    frame.loc[0, "bid"] = -1.0
    frame.loc[1, "ask"] = 0.0
    frame.loc[2, "vendor_delta"] = 5.0

    result = audit_standardized_options(frame)

    codes = {record["code"] for record in result.failures}
    assert {"NEGATIVE_BID", "NON_POSITIVE_ASK", "VENDOR_DELTA_OUT_OF_RANGE"} <= codes
    assert dict((row["metric"], row["value"]) for row in result.summary)["row_count"] == 4


def test_nearest_tenor_uses_shorter_dte_tie_and_computes_changes() -> None:
    rows = []
    for quote_date, iv in (("2022-01-03", 0.20), ("2022-01-04", 0.21)):
        for dte in (20, 22):
            rows.append(
                {
                    "underlying": "SPY",
                    "quote_date": quote_date,
                    "expiration": pd.Timestamp(quote_date) + pd.Timedelta(days=dte),
                    "actual_dte": dte,
                    "atm_mid_iv": iv,
                    "atm_bid_iv": iv - 0.01,
                    "atm_ask_iv": iv + 0.01,
                    "atm_total_variance": iv * iv * dte / 365.0,
                    "atm_mid_status": "SUCCESS",
                    "selected_point_count": 5,
                }
            )
    panel = build_nearest_tenor_panel(
        pd.DataFrame(rows), target_tenors=(21,), tenor_tolerances=(2,)
    )

    assert panel["actual_dte"].tolist() == [20, 20]
    assert panel.loc[1, "delta_atm_iv"] == pytest.approx(0.01)
    assert panel.loc[1, "noise_adjusted_move"] == pytest.approx(0.5)


def test_cross_split_change_is_suppressed() -> None:
    panel = pd.DataFrame(
        {
            "underlying": ["TSLA", "TSLA"],
            "target_tenor": [21, 21],
            "quote_date": ["2022-08-24", "2022-08-25"],
            "atm_mid_iv": [0.60, 0.61],
            "atm_total_variance": [0.02, 0.021],
            "atm_iv_spread": [0.02, 0.02],
        }
    )
    result = add_daily_stability(
        panel,
        group_columns=("underlying", "target_tenor"),
        split_dates=(("TSLA", "2022-08-25"),),
    )
    assert result.loc[1, "crosses_split"]
    assert pd.isna(result.loc[1, "delta_atm_iv"])


def test_config_hash_is_stable_and_validates_parallel_tuples(tmp_path) -> None:
    config = Research001Config(
        dataset_ids=("spy-pilot",),
        start_date=date(2020, 1, 1),
        end_date=date(2022, 12, 31),
        underlyings=("SPY",),
    )
    first = config.write(tmp_path / "first.json")
    second = config.write(tmp_path / "second.json")
    assert first.read_bytes() == second.read_bytes()
    assert len(config.sha256) == 64

    with pytest.raises(ValueError, match="requires one tolerance"):
        Research001Config(
            dataset_ids=("spy",),
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 2),
            underlyings=("SPY",),
            target_tenors=(21, 45),
            tenor_tolerances=(7,),
        )


def test_interpolated_zero_rate_curve_uses_flat_endpoints_and_linear_interior() -> None:
    curve = InterpolatedZeroRateCurve((0.25, 0.5, 1.0), (0.02, 0.03, 0.05))

    assert curve.zero_rate(0.10) == pytest.approx(0.02)
    assert curve.zero_rate(0.375) == pytest.approx(0.025)
    assert curve.zero_rate(2.0) == pytest.approx(0.05)
    assert curve.discount_factor(0.5) == pytest.approx(math.exp(-0.03 * 0.5))


def test_projected_dividend_schedule_does_not_use_future_amounts() -> None:
    distributions = pd.DataFrame(
        {
            "ex_date": pd.to_datetime(["2019-12-20", "2020-03-20", "2020-06-19"]),
            "cash_dividend": [1.20, 1.40, 1.35],
        }
    )

    dates, amounts = projected_dividend_schedule(
        distributions,
        quote_date=date(2020, 1, 2),
    )

    assert dates[:2] == (date(2020, 3, 20), date(2020, 6, 19))
    assert amounts[:2] == (1.20, 1.20)
    assert trailing_dividend_cash(distributions, date(2020, 3, 20)) == pytest.approx(2.60)


def test_cash_dividend_curve_respects_ex_date_timing() -> None:
    risk_curve = InterpolatedZeroRateCurve((0.25, 1.0), (0.02, 0.02))
    curve = CashDividendScheduleCurve(
        quote_date=date(2020, 1, 2),
        spot=100.0,
        ex_dates=(date(2020, 3, 20), date(2020, 6, 19)),
        cash_amounts=(1.0, 1.0),
        risk_free_curve=risk_curve,
    )

    assert curve.discount_factor(30 / 365) == pytest.approx(1.0)
    dividend_maturity = (date(2020, 3, 20) - date(2020, 1, 2)).days / 365
    expected = (100.0 - math.exp(-0.02 * dividend_maturity)) / 100.0
    assert curve.discount_factor(90 / 365) == pytest.approx(expected)
