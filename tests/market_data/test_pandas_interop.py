from datetime import date, datetime, timezone

import pytest

pd = pytest.importorskip("pandas")

from ncx_derivatives.market_data import (  # noqa: E402
    CarryAssumptions,
    CleaningConfig,
    ExerciseStyle,
    FlatDividendYieldCurve,
    FlatZeroRateCurve,
    NoArbitrageBounds,
    OptionChainSnapshot,
    OptionContract,
    OptionQuote,
    OptionType,
    SourceMetadata,
    StaticArbitrageConfig,
    StaticArbitrageCode,
    UnderlyingQuote,
    clean_option_chain,
    cleaning_result_to_dataframe,
    cleaning_result_to_records,
    diagnose_static_arbitrage,
    enrich_option_chain_snapshot,
    enriched_quotes_to_dataframe,
    enriched_quotes_to_records,
    option_chain_from_dataframe,
    option_chain_from_records,
    option_chain_to_dataframe,
    option_chain_to_records,
    static_arbitrage_report_to_dataframe,
    static_arbitrage_report_to_records,
    validate_option_chain_snapshot,
    validation_report_to_dataframe,
    validation_report_to_records,
)


UTC = timezone.utc
AS_OF = datetime(2026, 7, 30, 14, 30, tzinfo=UTC)


def _contract(option_type: OptionType, strike: float) -> OptionContract:
    return OptionContract(
        underlying_symbol="AAPL",
        expiration=date(2026, 8, 21),
        strike=strike,
        option_type=option_type,
        exercise_style=ExerciseStyle.EUROPEAN,
        contract_multiplier=100.0,
        currency="USD",
        source_contract_id=f"{option_type.value}-{strike}",
        display_symbol=f"AAPL {option_type.value} {strike}",
        listing_exchange="OPRA",
        metadata=SourceMetadata(provider="fixture"),
    )


def _snapshot() -> OptionChainSnapshot:
    return OptionChainSnapshot(
        underlying_symbol="AAPL",
        as_of=AS_OF,
        quotes=(
            OptionQuote(
                contract=_contract(OptionType.PUT, 95.0),
                quote_timestamp=AS_OF,
                bid=1.9,
                ask=2.1,
                bid_size=10,
                ask_size=11,
                session_volume=100,
                open_interest=500,
                open_interest_date=date(2026, 7, 29),
                metadata=SourceMetadata(provider="fixture", dataset="quotes"),
            ),
            OptionQuote(
                contract=_contract(OptionType.CALL, 100.0),
                quote_timestamp=AS_OF,
                bid=4.9,
                ask=5.1,
                bid_size=12,
                ask_size=14,
                session_volume=200,
                open_interest=600,
                open_interest_date=date(2026, 7, 29),
                metadata=SourceMetadata(provider="fixture", dataset="quotes"),
            ),
        ),
        underlying_quote=UnderlyingQuote(
            symbol="AAPL",
            quote_timestamp=AS_OF,
            price=101.0,
            bid=100.99,
            ask=101.01,
        ),
        metadata=SourceMetadata(provider="fixture", dataset="snapshot"),
    )


def _enriched_quotes():
    return enrich_option_chain_snapshot(
        snapshot=_snapshot(),
        carry=CarryAssumptions(
            risk_free_curve=FlatZeroRateCurve(0.04),
            dividend_curve=FlatDividendYieldCurve(0.01),
        ),
        valuation_date=date(2026, 7, 30),
    )


def test_option_chain_records_round_trip_to_snapshot() -> None:
    snapshot = _snapshot()

    records = option_chain_to_records(snapshot)
    restored = option_chain_from_records(records)

    assert len(records) == 2
    assert restored.underlying_symbol == snapshot.underlying_symbol
    assert restored.as_of == snapshot.as_of
    assert restored.quotes == snapshot.quotes
    assert restored.underlying_quote == snapshot.underlying_quote


def test_option_chain_dataframe_round_trip_to_snapshot() -> None:
    snapshot = _snapshot()

    frame = option_chain_to_dataframe(snapshot)
    restored = option_chain_from_dataframe(frame)

    assert isinstance(frame, pd.DataFrame)
    assert list(frame["strike"]) == [95.0, 100.0]
    assert restored.quotes == snapshot.quotes


def test_option_chain_from_dataframe_handles_nullable_integer_missing_values() -> None:
    frame = option_chain_to_dataframe(_snapshot())
    frame["open_interest"] = frame["open_interest"].astype("Int64")
    frame.loc[0, "open_interest"] = pd.NA

    restored = option_chain_from_dataframe(frame)

    assert restored.quotes[0].open_interest is None


def test_option_chain_from_dataframe_handles_nullable_string_missing_values() -> None:
    frame = option_chain_to_dataframe(_snapshot())
    frame["display_symbol"] = frame["display_symbol"].astype("string")
    frame.loc[0, "display_symbol"] = pd.NA

    restored = option_chain_from_dataframe(frame)

    assert restored.quotes[0].contract.display_symbol is None


def test_option_chain_from_dataframe_handles_nat_missing_values() -> None:
    frame = option_chain_to_dataframe(_snapshot())
    frame.loc[0, "open_interest_date"] = pd.NaT

    restored = option_chain_from_dataframe(frame)

    assert restored.quotes[0].open_interest_date is None


def test_enriched_quotes_to_records_and_dataframe() -> None:
    enriched = _enriched_quotes()

    records = enriched_quotes_to_records(enriched)
    frame = enriched_quotes_to_dataframe(enriched)

    assert len(records) == 2
    assert "underlying_symbol" in frame.columns
    assert "bid" in frame.columns
    assert "ask" in frame.columns
    assert "quote_timestamp" in frame.columns
    assert "contract_multiplier" in frame.columns
    assert "open_interest" in frame.columns
    assert "forward_price" in frame.columns
    assert "time_value" in frame.columns
    assert list(frame["option_type"]) == ["put", "call"]


def test_validation_report_to_records_and_dataframe() -> None:
    report = validate_option_chain_snapshot(
        OptionChainSnapshot(
            underlying_symbol="AAPL",
            as_of=AS_OF,
            quotes=(),
        ),
    )

    records = validation_report_to_records(report)
    frame = validation_report_to_dataframe(report)

    assert records
    assert "severity" in frame.columns
    assert "code" in frame.columns


def test_cleaning_result_to_records_and_dataframe() -> None:
    snapshot = OptionChainSnapshot(
        underlying_symbol="AAPL",
        as_of=AS_OF,
        quotes=(
            OptionQuote(
                contract=_contract(OptionType.CALL, 100.0),
                quote_timestamp=AS_OF,
                bid=None,
                ask=5.1,
            ),
        ),
    )
    result = clean_option_chain(snapshot)

    records = cleaning_result_to_records(result)
    frame = cleaning_result_to_dataframe(result)

    assert records[0]["reason"] == "MISSING_BID"
    assert list(frame["reason"]) == ["MISSING_BID"]


def test_static_arbitrage_report_to_records_and_dataframe() -> None:
    enriched = _enriched_quotes()[0]
    bad = type(enriched)(
        quote=enriched.quote,
        valuation_timestamp=enriched.valuation_timestamp,
        valuation_date=enriched.valuation_date,
        spot_price=enriched.spot_price,
        time_to_maturity=enriched.time_to_maturity,
        midpoint=500.0,
        absolute_spread=enriched.absolute_spread,
        relative_spread=enriched.relative_spread,
        risk_free_discount_factor=enriched.risk_free_discount_factor,
        dividend_discount_factor=enriched.dividend_discount_factor,
        forward_price=enriched.forward_price,
        spot_moneyness=enriched.spot_moneyness,
        forward_moneyness=enriched.forward_moneyness,
        log_moneyness=enriched.log_moneyness,
        intrinsic_value=enriched.intrinsic_value,
        time_value=enriched.time_value,
        no_arbitrage_bounds=NoArbitrageBounds(0.0, 10.0),
    )
    report = diagnose_static_arbitrage(
        (bad,),
        StaticArbitrageConfig(enable_call_put_parity=False),
    )

    records = static_arbitrage_report_to_records(report)
    frame = static_arbitrage_report_to_dataframe(report)

    assert records[0]["code"] == StaticArbitrageCode.PRICE_ABOVE_UPPER_BOUND.value
    assert frame.iloc[0]["violation_amount"] == pytest.approx(490.0)


def test_pandas_interop_validates_inputs() -> None:
    with pytest.raises(ValueError, match="snapshot"):
        option_chain_to_records("invalid")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="records"):
        option_chain_from_records(())

    with pytest.raises(ValueError, match="frame"):
        option_chain_from_dataframe("invalid")

    records = option_chain_to_records(_snapshot())
    with pytest.raises(ValueError, match="mapping objects"):
        option_chain_from_records((records[0], "invalid"))  # type: ignore[arg-type]


def test_records_api_does_not_require_pandas_for_missing_detection(monkeypatch) -> None:
    def fail_import():
        raise RuntimeError("pandas unavailable")

    import ncx_derivatives.market_data.pandas_interop as interop

    monkeypatch.setattr(interop, "_import_pandas", fail_import)

    records = option_chain_to_records(_snapshot())
    restored = option_chain_from_records(records)

    assert restored.quotes == _snapshot().quotes


def test_option_chain_from_records_rejects_inconsistent_snapshot_metadata() -> None:
    records = [dict(row) for row in option_chain_to_records(_snapshot())]
    records[1]["snapshot_dataset"] = "different"

    with pytest.raises(ValueError, match="snapshot metadata"):
        option_chain_from_records(records)


def test_option_chain_from_records_rejects_inconsistent_underlying_quote() -> None:
    records = [dict(row) for row in option_chain_to_records(_snapshot())]
    records[1]["underlying_price"] = 105.0

    with pytest.raises(ValueError, match="underlying quote"):
        option_chain_from_records(records)


def test_empty_dataframe_outputs_have_stable_columns() -> None:
    empty_enriched = enriched_quotes_to_dataframe(())
    empty_validation = validation_report_to_dataframe(type(validate_option_chain_snapshot(_snapshot()))())
    clean = clean_option_chain(
        OptionChainSnapshot(
            underlying_symbol="AAPL",
            as_of=AS_OF,
            quotes=(_snapshot().quotes[0],),
        ),
        CleaningConfig(reject_missing_bid=False, reject_missing_ask=False),
    )
    empty_cleaning = cleaning_result_to_dataframe(clean)
    empty_arbitrage = static_arbitrage_report_to_dataframe(
        type(diagnose_static_arbitrage(()))(),
    )

    assert "forward_price" in empty_enriched.columns
    assert "severity" in empty_validation.columns
    assert "reason" in empty_cleaning.columns
    assert "violation_amount" in empty_arbitrage.columns


def test_non_finite_numeric_records_are_rejected() -> None:
    records = [dict(row) for row in option_chain_to_records(_snapshot())]
    records[0]["bid"] = float("inf")

    with pytest.raises(ValueError, match="finite"):
        option_chain_from_records(records)

    records = [dict(row) for row in option_chain_to_records(_snapshot())]
    records[0]["bid_size"] = float("inf")

    with pytest.raises(ValueError, match="finite"):
        option_chain_from_records(records)


def test_empty_snapshot_records_round_trip_is_intentionally_unsupported() -> None:
    snapshot = OptionChainSnapshot(
        underlying_symbol="AAPL",
        as_of=AS_OF,
        quotes=(),
    )

    assert option_chain_to_records(snapshot) == ()
    with pytest.raises(ValueError, match="records must not be empty"):
        option_chain_from_records(option_chain_to_records(snapshot))
