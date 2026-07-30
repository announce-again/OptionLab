"""Validate a canonical option-chain snapshot.

This example uses explicit canonical models.

Provider normalisation is introduced in Stage 2.4.
"""

from datetime import date, datetime, timezone

from ncx_derivatives.market_data import (
    ExerciseStyle,
    OptionChainSnapshot,
    OptionContract,
    OptionQuote,
    OptionType,
    validate_option_chain_snapshot,
)


def main() -> None:
    as_of = datetime(2026, 7, 30, 14, 30, tzinfo=timezone.utc)
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
        as_of=as_of,
        quotes=(
            OptionQuote(
                contract=call,
                quote_timestamp=as_of,
                bid=5.10,
                ask=5.00,
            ),
            OptionQuote(
                contract=put,
                quote_timestamp=as_of,
                bid=None,
                ask=3.85,
            ),
        ),
    )

    report = validate_option_chain_snapshot(snapshot)

    print("Valid:", report.is_valid)
    print("Errors:", len(report.errors))
    for issue in report.errors:
        print("-", issue.code, issue.location, issue.message)

    print("Warnings:", len(report.warnings))
    for issue in report.warnings:
        print("-", issue.code, issue.location, issue.message)

    print("Info:", len(report.infos))
    for issue in report.infos:
        print("-", issue.code, issue.location, issue.message)


if __name__ == "__main__":
    main()

