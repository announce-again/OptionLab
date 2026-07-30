"""Build a canonical option-chain snapshot manually."""

from datetime import date, datetime, timezone

from ncx_derivatives.market_data import (
    ExerciseStyle,
    OptionChainSnapshot,
    OptionContract,
    OptionQuote,
    OptionType,
    UnderlyingQuote,
)


def main() -> None:
    timestamp = datetime(2026, 7, 30, 14, 30, tzinfo=timezone.utc)

    call = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=180.0,
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
    )
    put = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=180.0,
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
    )

    snapshot = OptionChainSnapshot(
        underlying_symbol="AAPL",
        as_of=timestamp,
        quotes=(
            OptionQuote(
                contract=put,
                quote_timestamp=timestamp,
                bid=3.70,
                ask=3.85,
            ),
            OptionQuote(
                contract=call,
                quote_timestamp=timestamp,
                bid=4.90,
                ask=5.05,
            ),
        ),
        underlying_quote=UnderlyingQuote(
            symbol="AAPL",
            quote_timestamp=timestamp,
            price=181.22,
            bid=181.20,
            ask=181.24,
        ),
    )

    print(f"Underlying: {snapshot.underlying_symbol}")
    print(f"As of: {snapshot.as_of.isoformat()}")
    print(f"Quotes: {len(snapshot.quotes)}")
    print(f"Contracts: {len(snapshot.contracts)}")
    print(f"Call and put pair: {call.pairing_key == put.pairing_key}")

    for quote in snapshot.quotes:
        print(
            quote.contract.option_type.value,
            quote.contract.strike,
            quote.bid,
            quote.ask,
        )


if __name__ == "__main__":
    main()
