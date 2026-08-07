from datetime import date

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
