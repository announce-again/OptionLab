"""Ingest and validate a Cboe-style option-chain fixture."""

from pathlib import Path

from ncx_derivatives.market_data import (
    SourceMetadata,
    cboe_option_intervals_csv_config,
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

    config = cboe_option_intervals_csv_config(
        source_metadata=SourceMetadata(
            provider="fixture",
            dataset="cboe-style-option-intervals",
        ),
        include_open_interest=True,
        include_calculated_underlying=True,
    )

    result = ingest_option_chain_csv(path, config)

    print(f"Raw rows: {len(result.raw_records)}")
    print(f"Successful rows: {result.successful_row_count}")
    print(f"Failed rows: {result.failed_row_count}")
    print(f"Snapshots: {len(result.snapshots)}")

    for index, snapshot in enumerate(result.snapshots):
        report = validate_option_chain_snapshot(snapshot)

        print()
        print(f"Snapshot {index + 1}")
        print(f"  As of: {snapshot.as_of.isoformat()}")
        print(f"  Quotes: {len(snapshot.quotes)}")
        print(f"  Errors: {len(report.errors)}")
        print(f"  Warnings: {len(report.warnings)}")
        print(f"  Infos: {len(report.infos)}")

        for issue in report.issues:
            location = "/".join(issue.location) or "<snapshot>"
            print(
                f"  [{issue.severity.value}] "
                f"{issue.code} at {location}: {issue.message}",
            )

    if result.errors:
        print("\nIngestion errors:")
        for error in result.errors:
            print(
                f"  row={error.row_number} "
                f"column={error.column} "
                f"code={error.code}: {error.message}",
            )


if __name__ == "__main__":
    main()
