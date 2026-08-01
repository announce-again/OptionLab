"""Generate synthetic quotes and run the complete Stage 3.1 pipeline."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from time import perf_counter

from ncx_derivatives.volatility import (
    SyntheticOptionDatasetConfig,
    run_csv_volatility_pipeline,
    synthetic_option_quote_csv_config,
    synthetic_volatility_pipeline_carry,
    synthetic_volatility_pipeline_cleaning_config,
    write_implied_volatility_chain_csv,
    write_synthetic_option_quote_csv,
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".tmp/examples_output/volatility_pipeline"),
    )
    return parser.parse_args()


def main() -> None:
    arguments = _arguments()
    config = SyntheticOptionDatasetConfig(
        row_count=arguments.rows,
        seed=arguments.seed,
    )
    source_path = arguments.output_dir / "synthetic_option_quotes.csv"
    iv_path = arguments.output_dir / "implied_volatility_chain.csv"

    generation_started = perf_counter()
    generated = write_synthetic_option_quote_csv(source_path, config)
    generation_seconds = perf_counter() - generation_started

    result = run_csv_volatility_pipeline(
        source_path,
        ingestion_config=synthetic_option_quote_csv_config(),
        carry=synthetic_volatility_pipeline_carry(config),
        valuation_date=config.valuation_date,
        cleaning_config=synthetic_volatility_pipeline_cleaning_config(),
    )

    export_started = perf_counter()
    exported = write_implied_volatility_chain_csv(
        iv_path,
        result.implied_volatility_chain,
    )
    export_seconds = perf_counter() - export_started
    counts = result.counts

    ingestion_codes = Counter(error.code for error in result.ingestion.errors)
    cleaning_reasons = Counter(
        diagnostic.reason.value for diagnostic in result.cleaning.diagnostics
    )
    iv_failure_reasons = Counter(
        iv_result.failure_reason.value
        for quote in result.implied_volatility_chain.quotes
        for iv_result in (quote.bid, quote.midpoint, quote.ask)
        if iv_result.failure_reason is not None
    )

    print(f"Generated input rows: {generated.row_count:,}")
    print(
        "Ingestion: "
        f"raw={counts.input_row_count:,}, "
        f"successful={counts.ingestion_success_count:,}, "
        f"failed_rows={counts.ingestion_failed_row_count:,}, "
        f"errors={counts.ingestion_error_count:,}, "
        f"snapshots={counts.snapshot_count:,}",
    )
    print(f"Enrichment: quotes={counts.enriched_quote_count:,}")
    print(
        "Cleaning: "
        f"accepted={counts.cleaning_accepted_count:,}, "
        f"rejected={counts.cleaning_rejected_count:,}, "
        f"diagnostics={counts.cleaning_diagnostic_count:,}",
    )
    print(
        "Stage 3.1 IV: "
        f"quotes={counts.iv_quote_count:,}, "
        f"results={counts.iv_result_count:,}, "
        f"successful={counts.iv_success_count:,}, "
        f"failed={counts.iv_failure_count:,}",
    )
    print(f"Export: rows={exported.row_count:,}, bytes={exported.byte_count:,}")
    print(f"Ingestion diagnostics: {dict(sorted(ingestion_codes.items()))}")
    print(f"Cleaning diagnostics: {dict(sorted(cleaning_reasons.items()))}")
    print(f"IV failure reasons: {dict(sorted(iv_failure_reasons.items()))}")
    print(
        "Timing seconds: "
        f"generation={generation_seconds:.3f}, "
        f"ingestion={result.timings.ingestion_seconds:.3f}, "
        f"enrichment={result.timings.enrichment_seconds:.3f}, "
        f"cleaning={result.timings.cleaning_seconds:.3f}, "
        f"iv={result.timings.implied_volatility_seconds:.3f}, "
        f"export={export_seconds:.3f}, "
        f"pipeline_total={result.timings.total_seconds:.3f}",
    )
    print(f"Pipeline throughput: {result.input_rows_per_second:,.0f} rows/second")
    print(f"Input: {source_path}")
    print(f"Output: {exported.path}")
    print(f"Output SHA-256: {exported.sha256}")


if __name__ == "__main__":
    main()
