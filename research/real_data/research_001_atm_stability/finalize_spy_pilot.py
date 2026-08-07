from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from research.real_data.common.deterministic_io import write_csv, write_output_hashes

from .analyse_spy import stability_summary
from .regressions import run_quote_uncertainty_regression, run_spy_regression


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize tables and interpretation from an existing SPY pilot panel")
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    finalize(arguments.output_dir)


def finalize(output_dir: Path) -> None:
    tenor = pd.read_parquet(output_dir / "atm_tenor_panel.parquet")
    expiry = pd.read_parquet(output_dir / "atm_expiry_panel.parquet")
    tenor["quote_date"] = pd.to_datetime(tenor["quote_date"])
    expiry["quote_date"] = pd.to_datetime(expiry["quote_date"])
    tenor["year"] = tenor["quote_date"].dt.year

    by_year = stability_summary(
        tenor,
        group_columns=("year", "target_tenor"),
        coverage_scope_columns=("year",),
    )
    write_csv(
        output_dir / "stability_by_year.csv",
        by_year.to_dict("records"),
        sort_by=("year", "target_tenor"),
    )

    regressions = []
    for model_name, runner in (
        ("spy_contemporaneous_hac", run_spy_regression),
        ("quote_uncertainty_next_day_hac", run_quote_uncertainty_regression),
    ):
        model, records = runner(tenor)
        regressions.extend({**record, "model": model_name} for record in records)
    write_csv(
        output_dir / "regression_results.csv",
        regressions,
        sort_by=("model", "term"),
    )

    quote_rows = []
    for target, group in tenor.groupby("target_tenor"):
        valid = group["noise_adjusted_move"].dropna()
        quote_rows.append(
            {
                "target_tenor": int(target),
                "observation_count": int(valid.size),
                "median_atm_iv_spread": group["atm_iv_spread"].median(),
                "median_absolute_atm_iv_change": group["absolute_atm_iv_change"].median(),
                "median_noise_adjusted_move": valid.median(),
                "fraction_move_within_average_iv_spread": (valid <= 1.0).mean(),
                "spearman_spread_vs_next_move": group["atm_iv_spread"].corr(
                    group["absolute_atm_iv_change"].shift(-1), method="spearman"
                ),
            }
        )
    quote_path = write_csv(
        output_dir / "quote_uncertainty_results.csv",
        quote_rows,
        sort_by=("target_tenor",),
    )

    robustness = []
    for target, group in tenor.groupby("target_tenor"):
        relative_variance_change = (
            group["delta_atm_total_variance"].abs()
            / group["previous_atm_total_variance"]
        )
        robustness.extend(
            (
                _robustness("nearest_tenor", target, "median_abs_atm_iv_change", group["absolute_atm_iv_change"].median()),
                _robustness("nearest_tenor", target, "median_abs_relative_atm_iv_change", group["relative_atm_iv_change"].abs().median()),
                _robustness("nearest_tenor", target, "median_abs_total_variance_change", group["delta_atm_total_variance"].abs().median()),
                _robustness("nearest_tenor", target, "median_abs_relative_total_variance_change", relative_variance_change.median()),
            )
        )
    robustness.extend(
        (
            _robustness("fixed_expiration_selected_sample", None, "median_abs_atm_iv_change", expiry["absolute_atm_iv_change"].median()),
            _robustness("nearest_tenor", None, "median_abs_atm_iv_change", tenor["absolute_atm_iv_change"].median()),
        )
    )
    for method, group in tenor.groupby("atm_method", dropna=False):
        robustness.append(
            _robustness(
                f"atm_method:{method}",
                None,
                "median_abs_atm_iv_change",
                group["absolute_atm_iv_change"].median(),
                observation_count=int(group["absolute_atm_iv_change"].count()),
            )
        )
    robustness_path = write_csv(
        output_dir / "robustness_results.csv",
        robustness,
        sort_by=("specification", "target_tenor", "metric"),
    )

    tenor_summary = pd.read_csv(output_dir / "stability_by_tenor.csv").set_index("target_tenor")
    year_summary = by_year.set_index(["year", "target_tenor"])
    regime_summary = pd.read_csv(output_dir / "stability_by_regime.csv")
    regression_frame = pd.DataFrame(regressions)
    next_spread = regression_frame.loc[
        (regression_frame["model"] == "quote_uncertainty_next_day_hac")
        & (regression_frame["term"] == "atm_iv_spread")
    ].iloc[0]
    extreme_21 = regime_summary.loc[
        (regime_summary["market_regime"] == "extreme")
        & (regime_summary["target_tenor"] == 21),
        "median_absolute_atm_iv_change",
    ].iloc[0]
    low_21 = regime_summary.loc[
        (regime_summary["market_regime"] == "low")
        & (regime_summary["target_tenor"] == 21),
        "median_absolute_atm_iv_change",
    ].iloc[0]
    findings = [
        {
            "hypothesis": "H1",
            "status": "supported_in_pilot",
            "evidence": f"Median |ΔATMIV| declines from {tenor_summary.loc[21, 'median_absolute_atm_iv_change']:.6f} at 21D to {tenor_summary.loc[150, 'median_absolute_atm_iv_change']:.6f} at 150D.",
        },
        {
            "hypothesis": "H2",
            "status": "supported_in_pilot",
            "evidence": f"Next-day ATM-spread HAC coefficient={next_spread['coefficient']:.6f}, p={next_spread['p_value']:.6g}.",
        },
        {
            "hypothesis": "H3",
            "status": "supported_descriptively",
            "evidence": f"21D extreme-regime median instability is {extreme_21/low_21:.2f}x the low-regime value.",
        },
        {
            "hypothesis": "H7",
            "status": "supported_ranking_differs",
            "evidence": _variance_ranking_evidence(robustness),
        },
        {
            "hypothesis": "H8",
            "status": "not_identified_by_pilot_design",
            "evidence": "The pilot preselected nearest expiries before inversion; its fixed-expiry subset is not a like-for-like full expiry panel.",
        },
    ]
    findings_path = write_csv(
        output_dir / "pilot_key_findings.csv",
        findings,
        columns=("hypothesis", "status", "evidence"),
        sort_by=("hypothesis",),
    )
    _write_report(
        output_dir / "research_001_report.md",
        tenor_summary=tenor_summary,
        year_summary=year_summary,
        quote_rows=quote_rows,
        findings=findings,
        next_spread=next_spread,
        extreme_ratio=extreme_21 / low_21,
    )
    write_output_hashes(output_dir, output_dir / "output_hashes.json")
    print(f"Wrote {quote_path}")
    print(f"Wrote {robustness_path}")
    print(f"Wrote {findings_path}")


def _robustness(specification, target_tenor, metric, value, observation_count=None):
    return {
        "specification": specification,
        "target_tenor": target_tenor,
        "metric": metric,
        "value": value,
        "observation_count": observation_count,
    }


def _variance_ranking_evidence(records) -> str:
    frame = pd.DataFrame(records)
    subset = frame.loc[
        (frame["specification"] == "nearest_tenor")
        & frame["target_tenor"].notna()
        & frame["metric"].isin(
            ["median_abs_relative_atm_iv_change", "median_abs_relative_total_variance_change"]
        )
    ]
    rankings = {
        metric: subset.loc[subset["metric"] == metric].sort_values("value")["target_tenor"].astype(int).tolist()
        for metric in subset["metric"].unique()
    }
    return f"Stability ranking from most to least stable: IV={rankings.get('median_abs_relative_atm_iv_change')}; total variance={rankings.get('median_abs_relative_total_variance_change')}."


def _write_report(path, *, tenor_summary, year_summary, quote_rows, findings, next_spread, extreme_ratio):
    quote_frame = pd.DataFrame(quote_rows).set_index("target_tenor")
    lines = [
        "# Research 001 Pilot A — SPY ATM volatility stability, 2020–2022",
        "",
        "## Status",
        "",
        "This is a completed Pilot A diagnostic, not the formal rate/dividend-enriched Research 001A result. "
        "NCX bid/mid/ask IV was reconstructed under zero rates and zero dividends after a recorded nearest-expiry and |log(K/S)| ≤ 0.40 prefilter.",
        "",
        "## Main findings",
        "",
        f"- Short maturity is less stable. Median daily |ΔATMIV| is {tenor_summary.loc[21, 'median_absolute_atm_iv_change']*100:.3f} volatility points at 21D, "
        f"{tenor_summary.loc[45, 'median_absolute_atm_iv_change']*100:.3f} at 45D, {tenor_summary.loc[90, 'median_absolute_atm_iv_change']*100:.3f} at 90D, and "
        f"{tenor_summary.loc[150, 'median_absolute_atm_iv_change']*100:.3f} at 150D.",
        f"- Stress matters strongly in the descriptive data. Extreme-regime 21D instability is {extreme_ratio:.2f}× the low-regime median.",
        f"- 2020 is the least stable year at 21D and 45D: medians are {year_summary.loc[(2020,21), 'median_absolute_atm_iv_change']*100:.3f} and "
        f"{year_summary.loc[(2020,45), 'median_absolute_atm_iv_change']*100:.3f} volatility points.",
        f"- Quote uncertainty predicts later movement in the pilot. The next-day HAC coefficient on ATM IV spread is {next_spread['coefficient']:.3f} "
        f"(p={next_spread['p_value']:.4g}). This is predictive association, not causality.",
        f"- Only {quote_frame.loc[21, 'fraction_move_within_average_iv_spread']:.1%} of valid 21D daily moves fall within the average current/previous ATM IV bid-ask interval; "
        f"the corresponding 150D fraction is {quote_frame.loc[150, 'fraction_move_within_average_iv_spread']:.1%}.",
        "",
        "## Coverage",
        "",
        f"The panel contains {int(tenor_summary['count'].sum()):,} observations. Coverage is {tenor_summary.loc[21, 'coverage']:.1%} at 21D, "
        f"{tenor_summary.loc[45, 'coverage']:.1%} at 45D, {tenor_summary.loc[90, 'coverage']:.1%} at 90D, and {tenor_summary.loc[150, 'coverage']:.1%} at 150D.",
        "",
        "## Interpretation limits",
        "",
        "- This pilot is deliberately labelled `zero_rate_zero_dividend_diagnostic`.",
        "- The pilot prefilter makes the fixed-expiry versus nearest-tenor comparison non-identifying.",
        "- SPY options are American-style while NCX inversion uses the current Black–Scholes research pipeline; the approximation must be retained as a limitation.",
        "- H4–H6 require the multi-underlying Part B datasets and are not tested here.",
        "- Formal Research 001A still requires the 2010–2023 dataset and historical rate/dividend enrichment.",
        "",
        "## Hypothesis log",
        "",
    ]
    lines.extend(f"- {item['hypothesis']}: {item['status']} — {item['evidence']}" for item in findings)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
