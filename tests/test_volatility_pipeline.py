from ncx_derivatives.volatility import (
    ImpliedVolatilityFailureReason,
    SyntheticOptionDatasetConfig,
    implied_volatility_chain_to_records,
    run_csv_volatility_pipeline,
    synthetic_option_quote_csv_config,
    synthetic_volatility_pipeline_carry,
    synthetic_volatility_pipeline_cleaning_config,
    write_implied_volatility_chain_csv,
    write_synthetic_option_quote_csv,
)


def test_medium_csv_to_iv_pipeline_is_deterministic_and_isolates_bad_rows(
    tmp_path,
) -> None:
    config = SyntheticOptionDatasetConfig(row_count=2_000)
    first_source = write_synthetic_option_quote_csv(tmp_path / "first.csv", config)
    second_source = write_synthetic_option_quote_csv(tmp_path / "second.csv", config)

    first = _run_pipeline(first_source.path, config)
    second = _run_pipeline(second_source.path, config)
    first_export = write_implied_volatility_chain_csv(
        tmp_path / "first-iv.csv",
        first.implied_volatility_chain,
    )
    second_export = write_implied_volatility_chain_csv(
        tmp_path / "second-iv.csv",
        second.implied_volatility_chain,
    )

    assert first_source.sha256 == second_source.sha256
    assert first_source.ingestion_bad_row_count == 1
    assert first_source.cleaning_bad_row_count == 2
    assert first_source.iv_bad_row_count == 1
    assert first.counts.input_row_count == 2_000
    assert first.counts.ingestion_success_count == 1_999
    assert first.counts.ingestion_failed_row_count == 1
    assert first.counts.snapshot_count == 4
    assert first.counts.enriched_quote_count == 1_999
    assert first.counts.cleaning_accepted_count == 1_997
    assert first.counts.cleaning_rejected_count == 2
    assert first.counts.cleaning_diagnostic_count == 2
    assert first.counts.iv_quote_count == 1_997
    assert first.counts.iv_result_count == 5_991
    assert first.counts.iv_success_count == 5_988
    assert first.counts.iv_failure_count == 3
    assert first.counts.iv_quote_with_failure_count == 1

    ingestion_error = first.ingestion.errors[0]
    assert ingestion_error.row_number > 1
    assert ingestion_error.raw_record is not None
    assert all(item.diagnostics for item in first.cleaning.rejected)
    assert {
        result.failure_reason
        for quote in first.implied_volatility_chain.quotes
        for result in (quote.bid, quote.midpoint, quote.ask)
        if result.failure_reason is not None
    } == {ImpliedVolatilityFailureReason.OUTSIDE_BOUNDS}

    assert implied_volatility_chain_to_records(first.implied_volatility_chain) == (
        implied_volatility_chain_to_records(second.implied_volatility_chain)
    )
    assert first_export.row_count == 1_997
    assert first_export.sha256 == second_export.sha256
    assert first_export.path.read_bytes() == second_export.path.read_bytes()
    assert first.counts.iv_success_count > first.counts.iv_failure_count


def _run_pipeline(path, config: SyntheticOptionDatasetConfig):
    return run_csv_volatility_pipeline(
        path,
        ingestion_config=synthetic_option_quote_csv_config(),
        carry=synthetic_volatility_pipeline_carry(config),
        valuation_date=config.valuation_date,
        cleaning_config=synthetic_volatility_pipeline_cleaning_config(),
    )
