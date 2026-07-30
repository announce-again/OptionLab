"""Enrich canonical option quotes with research fields."""

from datetime import date
from pathlib import Path

from ncx_derivatives.market_data import (
    CarryAssumptions,
    FlatDividendYieldCurve,
    FlatZeroRateCurve,
    SourceMetadata,
    cboe_option_intervals_csv_config,
    enrich_option_chain_snapshot,
    ingest_option_chain_csv,
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

    snapshot = ingestion.snapshots[0]
    enriched_quotes = enrich_option_chain_snapshot(
        snapshot=snapshot,
        carry=carry,
        valuation_date=date(2026, 7, 30),
    )

    print(f"Underlying: {snapshot.underlying_symbol}")
    print(f"As of: {snapshot.as_of.isoformat()}")
    print()

    for item in enriched_quotes:
        contract = item.quote.contract
        print(
            f"{contract.option_type.value.upper():4} "
            f"K={contract.strike:7.2f} "
            f"mid={item.midpoint!s:>6} "
            f"spread={item.relative_spread!s:>8} "
            f"T={item.time_to_maturity:.6f} "
            f"F={item.forward_price:.4f} "
            f"F/K={item.forward_moneyness:.4f} "
            f"intrinsic={item.intrinsic_value:.4f} "
            f"time_value={item.time_value}",
        )


if __name__ == "__main__":
    main()
