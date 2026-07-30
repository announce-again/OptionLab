# ncx_derivatives Examples

Run examples from the repository root after installing the package in editable
mode:

```powershell
python -m pip install -e .
python examples/stage_1/01_black_scholes_pricing.py
python examples/market_data/build_canonical_snapshot.py
python examples/market_data/ingest_and_validate_csv.py
python examples/market_data/enrich_option_chain.py
python examples/market_data/clean_option_chain.py
```

The market-data examples use small synthetic or reconstructed fixtures and do
not require network access, provider credentials, or pandas.

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
2. CSV ingestion and validation
3. Rates, forwards, and derived fields
4. Configurable cleaning with rejection diagnostics

- `market_data/build_canonical_snapshot.py` - manual canonical snapshot construction
- `market_data/ingest_and_validate_csv.py` - Cboe-style fixture ingestion and validation
- `market_data/enrich_option_chain.py` - rates, forwards, moneyness, spreads, and value decomposition
- `market_data/clean_option_chain.py` - end-to-end ingestion, validation, enrichment, and cleaning
