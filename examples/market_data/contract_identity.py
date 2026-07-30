from datetime import date

from ncx_derivatives.market_data import (
    ExerciseStyle,
    OptionContract,
    OptionType,
    SourceMetadata,
)


def main() -> None:
    provider_a_contract = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 9, 18),
        strike=200.0,
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="provider-a-id",
        display_symbol="AAPL_PROVIDER_A",
        metadata=SourceMetadata(provider="provider_a"),
    )
    provider_b_contract = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 9, 18),
        strike=200.0,
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="provider-b-id",
        display_symbol="AAPL_PROVIDER_B",
        metadata=SourceMetadata(provider="provider_b"),
    )

    matching_put = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 9, 18),
        strike=200.0,
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id="provider-put-id",
    )
    adjusted_put = OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 9, 18),
        strike=200.0,
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.AMERICAN,
        contract_multiplier=10.0,
        currency="USD",
        source_contract_id="adjusted-provider-put-id",
    )

    print(
        "Same economic contract despite provider metadata:",
        provider_a_contract == provider_b_contract,
    )
    print(
        "Same hash despite provider metadata:",
        hash(provider_a_contract) == hash(provider_b_contract),
    )
    print(
        "Call and matching put pairing key equal:",
        provider_a_contract.pairing_key == matching_put.pairing_key,
    )
    print(
        "Different multiplier pairing key equal:",
        provider_a_contract.pairing_key == adjusted_put.pairing_key,
    )


if __name__ == "__main__":
    main()

