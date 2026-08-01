from time import perf_counter

import pytest

from ncx_derivatives.volatility import (
    SyntheticOptionDatasetConfig,
    run_csv_volatility_pipeline,
    synthetic_option_quote_csv_config,
    synthetic_volatility_pipeline_carry,
    synthetic_volatility_pipeline_cleaning_config,
    write_implied_volatility_chain_csv,
    write_synthetic_option_quote_csv,
)


@pytest.mark.large
def test_large_50k_csv_to_iv_pipeline_smoke_and_throughput(
    tmp_path,
    record_property,
) -> None:
    config = SyntheticOptionDatasetConfig(row_count=50_000)
    source = write_synthetic_option_quote_csv(tmp_path / "quotes-50k.csv", config)

    started = perf_counter()
    result = run_csv_volatility_pipeline(
        source.path,
        ingestion_config=synthetic_option_quote_csv_config(),
        carry=synthetic_volatility_pipeline_carry(config),
        valuation_date=config.valuation_date,
        cleaning_config=synthetic_volatility_pipeline_cleaning_config(),
    )
    exported = write_implied_volatility_chain_csv(
        tmp_path / "iv-chain-50k.csv",
        result.implied_volatility_chain,
    )
    elapsed_seconds = perf_counter() - started
    throughput = config.row_count / elapsed_seconds
    record_property("rows", config.row_count)
    record_property("elapsed_seconds", elapsed_seconds)
    record_property("rows_per_second", throughput)

    assert source.ingestion_bad_row_count == 5
    assert source.cleaning_bad_row_count == 10
    assert source.iv_bad_row_count == 5
    assert result.counts.input_row_count == 50_000
    assert result.counts.ingestion_failed_row_count == 5
    assert result.counts.snapshot_count == 100
    assert result.counts.enriched_quote_count == 49_995
    assert result.counts.cleaning_rejected_count == 10
    assert result.counts.cleaning_accepted_count == 49_985
    assert result.counts.iv_quote_count == 49_985
    assert result.counts.iv_failure_count == 15
    assert exported.row_count == 49_985
    assert exported.byte_count > 0
    assert throughput > 100.0
