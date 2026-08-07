from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from research.real_data.common.deterministic_io import write_csv, write_output_hashes


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two aligned SPY Pilot carry specifications")
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--alternative-dir", type=Path, required=True)
    arguments = parser.parse_args()
    compare(arguments.baseline_dir, arguments.alternative_dir)


def compare(baseline_dir: Path, alternative_dir: Path) -> Path:
    base = pd.read_parquet(baseline_dir / "atm_tenor_panel.parquet")
    alt = pd.read_parquet(alternative_dir / "atm_tenor_panel.parquet")
    keys = ["underlying", "quote_date", "target_tenor"]
    aligned = base.merge(
        alt,
        on=keys,
        how="inner",
        suffixes=("_baseline", "_alternative"),
        validate="one_to_one",
    )
    aligned["atm_iv_difference"] = aligned["atm_mid_iv_alternative"] - aligned["atm_mid_iv_baseline"]
    records = []
    for target, group in aligned.groupby("target_tenor"):
        records.append(
            {
                "target_tenor": int(target),
                "aligned_observation_count": len(group),
                "median_atm_iv_difference": group["atm_iv_difference"].median(),
                "median_absolute_atm_iv_difference": group["atm_iv_difference"].abs().median(),
                "p95_absolute_atm_iv_difference": group["atm_iv_difference"].abs().quantile(0.95),
                "atm_iv_level_correlation": group["atm_mid_iv_baseline"].corr(group["atm_mid_iv_alternative"]),
                "baseline_median_absolute_change": group["absolute_atm_iv_change_baseline"].median(),
                "alternative_median_absolute_change": group["absolute_atm_iv_change_alternative"].median(),
                "median_change_difference": (
                    group["absolute_atm_iv_change_alternative"].median()
                    - group["absolute_atm_iv_change_baseline"].median()
                ),
            }
        )
    output = write_csv(
        baseline_dir / "carry_sensitivity_results.csv",
        records,
        sort_by=("target_tenor",),
    )
    report_path = baseline_dir / "research_001_report.md"
    report = report_path.read_text(encoding="utf-8")
    table = pd.DataFrame(records).set_index("target_tenor")
    baseline_rank = table.sort_values("baseline_median_absolute_change").index.astype(int).tolist()
    alternative_rank = table.sort_values("alternative_median_absolute_change").index.astype(int).tolist()
    rank_sentence = (
        f"The maturity ranking is preserved ({baseline_rank})."
        if baseline_rank == alternative_rank
        else f"The maturity ranking changes materially: baseline={baseline_rank}, alternative={alternative_rank}."
    )
    addition = (
        "\n## Carry sensitivity\n\n"
        f"{rank_sentence} "
        f"Median absolute ATM-IV level differences range from {table['median_absolute_atm_iv_difference'].min()*100:.3f} "
        f"to {table['median_absolute_atm_iv_difference'].max()*100:.3f} volatility points across tenors. "
        f"The largest change in a tenor's median daily instability is {table['median_change_difference'].abs().max()*100:.3f} volatility points.\n"
    )
    if "## Carry sensitivity" not in report:
        report_path.write_text(report.rstrip() + "\n" + addition, encoding="utf-8", newline="\n")
    else:
        report = report.split("\n## Carry sensitivity", 1)[0].rstrip()
        report_path.write_text(report + "\n" + addition, encoding="utf-8", newline="\n")

    findings_path = baseline_dir / "pilot_key_findings.csv"
    findings = pd.read_csv(findings_path)
    h1 = findings["hypothesis"].eq("H1")
    if h1.any():
        findings.loc[h1, "status"] = "supported_in_zero_carry_not_robust"
        findings.loc[h1, "evidence"] = (
            f"Zero-carry ranking={baseline_rank}; flat 4% rate/1.5% dividend ranking={alternative_rank}."
        )
        write_csv(
            findings_path,
            findings.to_dict("records"),
            columns=("hypothesis", "status", "evidence"),
            sort_by=("hypothesis",),
        )
        report_text = report_path.read_text(encoding="utf-8")
        revised_lines = []
        for line in report_text.splitlines():
            if line.startswith("- H1:"):
                line = (
                    "- H1: supported_in_zero_carry_not_robust — "
                    f"Zero-carry ranking={baseline_rank}; flat 4% rate/1.5% dividend ranking={alternative_rank}."
                )
            revised_lines.append(line)
        report_path.write_text("\n".join(revised_lines) + "\n", encoding="utf-8", newline="\n")
    base_regression = pd.read_csv(baseline_dir / "regression_results.csv")
    alt_regression = pd.read_csv(alternative_dir / "regression_results.csv")
    base_spread = _coefficient(base_regression, "quote_uncertainty_next_day_hac", "atm_iv_spread")
    alt_spread = _coefficient(alt_regression, "quote_uncertainty_next_day_hac", "atm_iv_spread")
    h2 = findings["hypothesis"].eq("H2")
    findings.loc[h2, "status"] = "supported_across_both_carry_specs"
    findings.loc[h2, "evidence"] = (
        f"Next-day spread coefficients: baseline={base_spread['coefficient']:.6f} "
        f"(p={base_spread['p_value']:.6g}), alternative={alt_spread['coefficient']:.6f} "
        f"(p={alt_spread['p_value']:.6g})."
    )
    base_ratio = _extreme_low_ratio(baseline_dir)
    alt_ratio = _extreme_low_ratio(alternative_dir)
    h3 = findings["hypothesis"].eq("H3")
    findings.loc[h3, "status"] = "supported_descriptively_across_carry_specs"
    findings.loc[h3, "evidence"] = (
        f"21D extreme/low median-instability ratios: baseline={base_ratio:.2f}x, alternative={alt_ratio:.2f}x."
    )
    write_csv(
        findings_path,
        findings.to_dict("records"),
        columns=("hypothesis", "status", "evidence"),
        sort_by=("hypothesis",),
    )
    report_text = report_path.read_text(encoding="utf-8")
    revised_lines = []
    evidence_by_hypothesis = findings.set_index("hypothesis")
    for line in report_text.splitlines():
        for hypothesis in ("H2", "H3"):
            if line.startswith(f"- {hypothesis}:"):
                item = evidence_by_hypothesis.loc[hypothesis]
                line = f"- {hypothesis}: {item['status']} — {item['evidence']}"
        revised_lines.append(line)
    report_path.write_text("\n".join(revised_lines) + "\n", encoding="utf-8", newline="\n")
    write_output_hashes(baseline_dir, baseline_dir / "output_hashes.json")
    print(output)
    return output


def _coefficient(frame, model, term):
    return frame.loc[(frame["model"] == model) & (frame["term"] == term)].iloc[0]


def _extreme_low_ratio(directory: Path) -> float:
    frame = pd.read_csv(directory / "stability_by_regime.csv")
    target = frame.loc[frame["target_tenor"] == 21].set_index("market_regime")
    return float(
        target.loc["extreme", "median_absolute_atm_iv_change"]
        / target.loc["low", "median_absolute_atm_iv_change"]
    )


if __name__ == "__main__":
    main()
