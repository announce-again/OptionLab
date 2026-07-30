"""Ingest a Cboe-style fixture through the market-data pipeline."""

from pathlib import Path

from ncx_derivatives.market_data import (
    SourceMetadata,
    cboe_option_intervals_csv_config,
    ingest_option_chain_csv,
    validate_option_chain_snapshot,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fixture_path = (
        repo_root
        / "tests"
        / "fixtures"
        / "market_data"
        / "cboe_intervals"
        / "normal.csv"
    )
    config = cboe_option_intervals_csv_config(
        source_metadata=SourceMetadata(
            provider="fixture",
            dataset="cboe_intervals",
            schema="cboe_option_intervals_with_calcs",
        ),
    )

    result = ingest_option_chain_csv(fixture_path, config)
    reports = [
        validate_option_chain_snapshot(snapshot)
        for snapshot in result.snapshots
    ]

    print("Fixture:", fixture_path)
    print("Snapshots:", len(result.snapshots))
    for index, snapshot in enumerate(result.snapshots, start=1):
        print(
            f"- snapshot {index}:",
            snapshot.as_of.isoformat(),
            "quotes:",
            len(snapshot.quotes),
        )

    print("Successful rows:", result.successful_row_count)
    print("Failed rows:", result.failed_row_count)
    print("Ingestion errors:", len(result.errors))
    print("Validation errors:", sum(len(report.errors) for report in reports))
    print(
        "Validation warnings:",
        sum(len(report.warnings) for report in reports),
    )

    print("First canonical quotes:")
    for snapshot in result.snapshots:
        for quote in snapshot.quotes[:3]:
            contract = quote.contract
            print(
                "-",
                snapshot.as_of.isoformat(),
                contract.option_type.value,
                contract.expiration.isoformat(),
                contract.strike,
                "bid:",
                quote.bid,
                "ask:",
                quote.ask,
                "timestamp UTC:",
                quote.quote_timestamp.isoformat(),
            )


if __name__ == "__main__":
    main()
