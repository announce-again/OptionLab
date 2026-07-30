"""Ingest a Cboe-style CSV fixture with explicit column mappings.

This example uses explicit CSV mappings.

Provider normalisation is introduced in Stage 2.4.
"""

from pathlib import Path

from ncx_derivatives.market_data import (
    CsvColumnMapping,
    CsvIngestionConfig,
    OptionType,
    SourceMetadata,
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

    mapping = CsvColumnMapping(
        underlying_symbol="Underlying Symbol",
        expiration="Expiration",
        strike="Strike",
        option_type="Option Type",
        quote_timestamp="Quote Datetime",
        bid="Bid",
        ask="Ask",
        bid_size="Bid Size",
        ask_size="Ask Size",
        open_interest="Open Interest",
        underlying_price="Active Underlying Price",
        underlying_bid="Underlying Bid",
        underlying_ask="Underlying Ask",
    )
    config = CsvIngestionConfig(
        mapping=mapping,
        source_metadata=SourceMetadata(
            provider="fixture",
            dataset="cboe_intervals",
            schema="explicit_mapping",
        ),
        option_type_values={"C": OptionType.CALL, "P": OptionType.PUT},
    )

    result = ingest_option_chain_csv(fixture_path, config)

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

    validation_reports = [
        validate_option_chain_snapshot(snapshot)
        for snapshot in result.snapshots
    ]
    validation_errors = sum(len(report.errors) for report in validation_reports)
    validation_warnings = sum(
        len(report.warnings)
        for report in validation_reports
    )

    print("Ingestion errors:", len(result.errors))
    print("Validation errors:", validation_errors)
    print("Validation warnings:", validation_warnings)

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
            )


if __name__ == "__main__":
    main()

