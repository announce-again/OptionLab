# Numerical Greeks

The numerical Greeks module provides model-independent bump-and-revalue
estimators for pricers that return either a float price or an object with a
`.price` attribute, such as `MonteCarloResult`.

## Public API

```python
from ncx_derivatives.greeks import numerical_delta
from ncx_derivatives.monte_carlo import monte_carlo_call_price

delta = numerical_delta(
    monte_carlo_call_price,
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
    bump=0.10,
    simulations=50_000,
    seed=42,
)
```

Available estimators:

- `numerical_delta`
- `numerical_gamma`
- `numerical_vega`
- `numerical_theta`
- `numerical_rho`

## Methods

First-order Greeks support central, forward, and backward differences. Gamma
supports central, forward, and backward second differences.

When `bump=None`, the estimator uses an adaptive relative bump:

```text
bump = relative_bump * max(abs(parameter), 1.0)
```

Set `return_diagnostics=True` to return `NumericalGreekResult` with the bump,
method, number of price evaluations, and raw bumped prices.

The adaptive bump is scale-aware, but it does not automatically change the
difference method or shrink the bump near hard parameter boundaries. Central
or backward differences that would push spot or strike to zero, or maturity or
volatility below zero, raise `ValueError`. Use a forward difference or explicit
smaller bump near those boundaries.

## Monte Carlo Notes

Common random numbers are supported by passing a fixed `seed` through the
pricing keyword arguments. The same seed is reused for each bumped valuation,
which materially reduces finite-difference noise for Monte Carlo pricers.

Monte Carlo Gamma is especially noisy because it is a second-order difference.
Use larger simulation counts, common random numbers, variance reduction, and
diagnostics when interpreting it.

## Future Extension

The single-Greek functions intentionally keep a small API. A future
`numerical_greeks(...)` batch estimator can reuse the base valuation across
Delta, Gamma, Vega, Theta, and Rho for expensive pricers.
