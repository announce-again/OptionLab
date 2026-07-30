"""Build canonical market-data objects by hand."""

from datetime import date, datetime, timezone

from ncx_derivatives.market_data import (
    ExerciseStyle,
    OptionChainSnapshot,
    OptionContract,
    OptionQuote,
    OptionType,
    SourceMetadata,
    UnderlyingQuote,
)


def main() -> None:
    as_of = datetime(2026, 7, 30, 14, 30, tzinfo=timezone.utc)
    metadata = SourceMetadata(provider="manual_example")

    call = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=180.0,
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="manual-call",
        display_symbol="AAPL  260821C00180000",
        metadata=metadata,
    )
    put = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=180.0,
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="manual-put",
        display_symbol="AAPL  260821P00180000",
        metadata=metadata,
    )

    snapshot = OptionChainSnapshot(
        underlying_symbol="AAPL",
        as_of=as_of,
        quotes=(
            OptionQuote(
                contract=put,
                quote_timestamp=as_of,
                bid=3.70,
                ask=3.85,
                bid_size=10,
                ask_size=11,
                open_interest=980,
                open_interest_date=date(2026, 7, 29),
                metadata=metadata,
            ),
            OptionQuote(
                contract=call,
                quote_timestamp=as_of,
                bid=4.90,
                ask=5.05,
                bid_size=12,
                ask_size=15,
                open_interest=1200,
                open_interest_date=date(2026, 7, 29),
                metadata=metadata,
            ),
        ),
        underlying_quote=UnderlyingQuote(
            symbol="AAPL",
            quote_timestamp=as_of,
            price=181.22,
            bid=181.20,
            ask=181.24,
            metadata=metadata,
        ),
        metadata=metadata,
    )

    print("Snapshot:", snapshot.underlying_symbol, snapshot.as_of.isoformat())
    print("Quote count:", len(snapshot.quotes))
    print("Contracts:")
    for contract in snapshot.contracts:
        print(
            "-",
            contract.option_type.value,
            contract.expiration.isoformat(),
            contract.strike,
            contract.display_symbol,
        )
    print("Pairing key:", call.pairing_key)
    print("Call and put pair:", call.pairing_key == put.pairing_key)


if __name__ == "__main__":
    main()
