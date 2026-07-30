"""Ingest, validate, enrich, and clean an option-chain fixture."""

from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from ncx_derivatives.market_data import (
    CarryAssumptions,
    CleaningConfig,
    FlatDividendYieldCurve,
    FlatZeroRateCurve,
    SourceMetadata,
    cboe_option_intervals_csv_config,
    clean_enriched_option_quotes,
    enrich_option_chain_snapshot,
    ingest_option_chain_csv,
    validate_option_chain_snapshot,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    path = (
        repo_root
        / "tests"
        / "fixtures"
        / "market_data"
        / "cboe_intervals"
        / "normal.csv"
    )

    ingestion = ingest_option_chain_csv(
        path,
        cboe_option_intervals_csv_config(
            source_metadata=SourceMetadata(
                provider="fixture",
                dataset="cboe-style-option-intervals",
            ),
            include_open_interest=True,
            include_calculated_underlying=True,
        ),
    )

    carry = CarryAssumptions(
        risk_free_curve=FlatZeroRateCurve(0.04),
        dividend_curve=FlatDividendYieldCurve(0.01),
    )
    cleaning_config = CleaningConfig(
        reject_missing_bid=True,
        reject_missing_ask=True,
        reject_crossed_market=True,
        reject_locked_market=False,
        reject_zero_midpoint=True,
        max_relative_spread=0.40,
        min_open_interest=1,
        max_quote_age=timedelta(minutes=5),
        min_maturity=0.0,
        max_maturity=1.0,
        min_forward_moneyness=0.75,
        max_forward_moneyness=1.25,
        min_option_price=0.01,
    )

    for snapshot_index, snapshot in enumerate(ingestion.snapshots, start=1):
        validation = validate_option_chain_snapshot(snapshot)
        enriched = enrich_option_chain_snapshot(
            snapshot=snapshot,
            carry=carry,
            valuation_date=date(2026, 7, 30),
        )
        cleaning = clean_enriched_option_quotes(
            enriched,
            config=cleaning_config,
        )

        print(f"Snapshot {snapshot_index}: {snapshot.as_of.isoformat()}")
        print(f"  Validation errors: {len(validation.errors)}")
        print(f"  Validation warnings: {len(validation.warnings)}")
        print(f"  Accepted quotes: {cleaning.accepted_count}")
        print(f"  Rejected quotes: {cleaning.rejected_count}")

        reason_counts = Counter(
            diagnostic.reason.value
            for diagnostic in cleaning.diagnostics
        )
        if reason_counts:
            print("  Rejection reasons:")
            for reason, count in sorted(reason_counts.items()):
                print(f"    {reason}: {count}")

        for rejected in cleaning.rejected:
            contract = rejected.quote.contract
            reasons = ", ".join(
                diagnostic.reason.value
                for diagnostic in rejected.diagnostics
            )
            print(
                f"  Rejected "
                f"{contract.option_type.value} "
                f"K={contract.strike}: {reasons}",
            )

        print()


if __name__ == "__main__":
    main()
