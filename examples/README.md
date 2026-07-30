# Examples

Run examples from the repository root after installing the package in editable
mode:

```powershell
python -m pip install -e .
python examples/stage_1/01_black_scholes_pricing.py
python examples/market_data/09_end_to_end_pipeline.py
```

The examples require no network access or provider credentials. Market-data
sample data is synthetic and deterministic. pandas is only required for the
pandas interoperability examples.

## Quick Start

First pricing example:

```powershell
python examples/stage_1/01_black_scholes_pricing.py
```

First complete market-data pipeline:

```powershell
python examples/market_data/09_end_to_end_pipeline.py
```

## Stage 1

- `stage_1/01_black_scholes_pricing.py` - Black-Scholes-Merton call and put pricing
- `stage_1/02_implied_volatility.py` - price-to-IV round trip
- `stage_1/03_binomial_american_option.py` - American put pricing and exercise boundary
- `stage_1/04_monte_carlo_pricing.py` - European Monte Carlo with confidence interval
- `stage_1/05_asian_option.py` - arithmetic Asian option Monte Carlo
- `stage_1/06_numerical_greeks.py` - bump-and-revalue Greeks for analytical and MC pricers

## Market Data

The market-data examples progressively demonstrate:

1. Canonical market-data objects
2. Provider-style CSV ingestion
3. Validation reports
4. Rates, forwards, and derived fields
5. Configurable cleaning with rejection diagnostics
6. Static-arbitrage diagnostics
7. pandas boundary conversions
8. Deterministic dataset serialisation
9. End-to-end Stage 2 pipeline

- `market_data/01_build_canonical_snapshot.py` - manual canonical snapshot construction
- `market_data/02_ingest_provider_csv.py` - provider-style CSV to canonical snapshots
- `market_data/03_validate_option_chain.py` - structured validation issues
- `market_data/04_enrich_option_chain.py` - rates, forwards, moneyness, spreads, and bounds
- `market_data/05_clean_option_chain.py` - accepted/rejected cleaning partitions
- `market_data/06_diagnose_static_arbitrage.py` - detect/report/quantify price inconsistencies
- `market_data/07_pandas_interoperability.py` - records/DataFrame round trips and simple research summaries
- `market_data/08_write_dataset_snapshot.py` - deterministic dataset manifests and hashes
- `market_data/09_end_to_end_pipeline.py` - full CSV-to-dataset Stage 2 pipeline

Generated dataset outputs are written under `.tmp/examples_output/`.

## Design Principles

- Examples require no network access.
- Outputs are deterministic for fixed inputs and timestamps.
- pandas is used only in pandas-specific examples.
- Sample market data is synthetic and not real historical market data.
