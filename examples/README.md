# Examples

These examples show the core Stage 1 pricing, volatility, Monte Carlo, and
Greek workflows.

Run from the repository root after installing the package in editable mode:

```bash
pip install -e .
python examples/stage_1/01_black_scholes_pricing.py
```

## Files

- `stage_1/01_black_scholes_pricing.py` - Black-Scholes-Merton call and put pricing
- `stage_1/02_implied_volatility.py` - price-to-IV round trip
- `stage_1/03_binomial_american_option.py` - American put pricing and exercise boundary
- `stage_1/04_monte_carlo_pricing.py` - European Monte Carlo with confidence interval
- `stage_1/05_asian_option.py` - arithmetic Asian option Monte Carlo
- `stage_1/06_numerical_greeks.py` - bump-and-revalue Greeks for analytical and MC pricers
