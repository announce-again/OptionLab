from math import exp

from ncx_derivatives.utils.black_scholes import d1, d2, norm_cdf


def _validate_inputs(
    S: float,
    K: float,
    T: float,
    sigma: float,
) -> None:
    if S <= 0.0:
        raise ValueError("spot must be positive")
    if K <= 0.0:
        raise ValueError("strike must be positive")
    if T < 0.0:
        raise ValueError("maturity must be non-negative")
    if sigma < 0.0:
        raise ValueError("volatility must be non-negative")


def call_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Black-Scholes-Merton European call option price.
    """
    _validate_inputs(spot, strike, maturity, volatility)

    if maturity == 0.0:
        return max(spot - strike, 0.0)
    if volatility == 0.0:
        discounted_strike = strike * exp(-rate * maturity)
        discounted_spot = spot * exp(-dividend_yield * maturity)
        return max(discounted_spot - discounted_strike, 0.0)

    discounted_spot = spot * exp(-dividend_yield * maturity)
    discounted_strike = strike * exp(-rate * maturity)
    d_1 = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    d_2 = d2(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    return (
        discounted_spot * norm_cdf(d_1)
        - discounted_strike * norm_cdf(d_2)
    )


def put_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Black-Scholes-Merton European put option price.
    """
    _validate_inputs(spot, strike, maturity, volatility)

    if maturity == 0.0:
        return max(strike - spot, 0.0)
    if volatility == 0.0:
        discounted_strike = strike * exp(-rate * maturity)
        discounted_spot = spot * exp(-dividend_yield * maturity)
        return max(discounted_strike - discounted_spot, 0.0)

    discounted_spot = spot * exp(-dividend_yield * maturity)
    discounted_strike = strike * exp(-rate * maturity)
    d_1 = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    d_2 = d2(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    return (
        discounted_strike * norm_cdf(-d_2)
        - discounted_spot * norm_cdf(-d_1)
    )
