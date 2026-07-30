# NCX Derivatives

A from-scratch quantitative derivatives pricing, volatility, risk, and
market-making platform.

## Current capabilities

- Black-Scholes-Merton European call and put pricing
- Continuous dividend yield support
- Analytical Delta, Gamma, Vega, Theta, and Rho
- Implied volatility inversion with a hybrid Newton-bisection solver
- Cox-Ross-Rubinstein binomial tree pricing
- European and American option support
- Optional American exercise-boundary extraction
- Monte Carlo European option pricing
- Standard errors and confidence intervals
- Antithetic variates and control variates
- No-arbitrage bounds and input validation
- Finite-difference validation of analytical Greeks
- Comprehensive automated test coverage with pytest

## Installation

```bash
pip install -e .
```

## Quick start

```python
from ncx_derivatives.greeks import call_delta, gamma, vega
from ncx_derivatives.monte_carlo import monte_carlo_call_price
from ncx_derivatives.pricing import binomial_put_price, call_price
from ncx_derivatives.volatility import call_implied_volatility

price = call_price(
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
)

delta = call_delta(
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
)

option_gamma = gamma(
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
)

option_vega = vega(
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
)

implied_volatility = call_implied_volatility(
    option_price=price,
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    dividend_yield=0.02,
)

american_put = binomial_put_price(
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
    steps=500,
    american=True,
)

monte_carlo_result = monte_carlo_call_price(
    spot=100.0,
    strike=100.0,
    maturity=1.0,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.02,
    simulations=50_000,
    seed=42,
    control_variate=True,
)
```

## Roadmap

- [x] Stage 1.1: Black-Scholes pricing
- [x] Stage 1.2: Analytical Greeks
- [x] Stage 1.3: Implied volatility solver
- [x] Stage 1.4: Continuous dividend yield
- [x] Stage 1.5: Binomial tree pricing
- [x] Stage 1.6a: GBM terminal simulation
- [x] Stage 1.6b: European Monte Carlo pricing
- [x] Stage 1.6c: Monte Carlo standard errors and confidence intervals
- [x] Stage 1.6d: Monte Carlo variance reduction
- [ ] Stage 1.7: Numerical Greeks
- [ ] Stage 3: Volatility surfaces
- [ ] Stage 5: Portfolio risk
- [ ] Stage 6: Market-making simulation

## Testing

```bash
pytest
```
