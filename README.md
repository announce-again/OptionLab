# NCX Derivatives

A from-scratch quantitative derivatives pricing, volatility, risk, and
market-making platform.

## Current capabilities

- Black-Scholes-Merton European call and put pricing
- Continuous dividend yield support
- Analytical Delta, Gamma, Vega, Theta, and Rho
- Implied volatility inversion with a hybrid Newton-bisection solver
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
from ncx_derivatives.pricing import call_price
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
```

## Roadmap

- [x] Black-Scholes-Merton pricing
- [x] Analytical Greeks
- [x] Implied volatility solver
- [ ] Binomial tree pricing
- [ ] Monte Carlo pricing
- [ ] Volatility surfaces
- [ ] Portfolio risk
- [ ] Market-making simulation

## Testing

```bash
pytest
```
