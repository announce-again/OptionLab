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
    metadata = SourceMetadata(provider="example_fixture")

    call_contract = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=180.0,
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="provider-call-id",
        display_symbol="AAPL  260821C00180000",
        metadata=metadata,
    )
    put_contract = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=180.0,
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="provider-put-id",
        display_symbol="AAPL  260821P00180000",
        metadata=metadata,
    )

    # Intentionally create quotes out of sorted order. The snapshot will sort
    # them deterministically by contract identity.
    put_quote = OptionQuote(
        contract=put_contract,
        quote_timestamp=as_of,
        bid=3.70,
        ask=3.85,
        bid_size=10,
        ask_size=11,
        open_interest=980,
        open_interest_date=date(2026, 7, 29),
        metadata=metadata,
    )
    call_quote = OptionQuote(
        contract=call_contract,
        quote_timestamp=as_of,
        bid=4.90,
        ask=5.05,
        bid_size=12,
        ask_size=15,
        open_interest=1200,
        open_interest_date=date(2026, 7, 29),
        metadata=metadata,
    )

    underlying_quote = UnderlyingQuote(
        symbol="AAPL",
        quote_timestamp=as_of,
        price=181.22,
        bid=181.20,
        ask=181.24,
        metadata=metadata,
    )

    snapshot = OptionChainSnapshot(
        underlying_symbol="AAPL",
        as_of=as_of,
        quotes=(put_quote, call_quote),
        underlying_quote=underlying_quote,
        metadata=metadata,
    )

    print("Snapshot:", snapshot.underlying_symbol, snapshot.as_of.isoformat())
    print("Underlying price:", snapshot.underlying_quote.price)
    print("Contracts:")
    for contract in snapshot.contracts:
        print(
            "-",
            contract.option_type.value,
            contract.expiration.isoformat(),
            contract.strike,
            contract.display_symbol,
        )

    print("Call-put pairing key:", call_contract.pairing_key)
    print(
        "Call and put share pairing key:",
        call_contract.pairing_key == put_contract.pairing_key,
    )

    print("Deterministic quote order:")
    for quote in snapshot.quotes:
        print("-", quote.contract.option_type.value, quote.bid, quote.ask)


if __name__ == "__main__":
    main()

