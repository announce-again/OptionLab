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
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
) -> float:
    """
    Black-Scholes European call option price.
    """
    _validate_inputs(S, K, T, sigma)

    if T == 0.0:
        return max(S - K, 0.0)
    if sigma == 0.0:
        discounted_strike = K * exp(-r * T)
        return max(S - discounted_strike, 0.0)

    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)

    return (
        S * norm_cdf(d_1)
        - K * exp(-r * T) * norm_cdf(d_2)
    )


def put_price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
) -> float:
    """
    Black-Scholes European put option price.
    """
    _validate_inputs(S, K, T, sigma)

    if T == 0.0:
        return max(K - S, 0.0)
    if sigma == 0.0:
        discounted_strike = K * exp(-r * T)
        return max(discounted_strike - S, 0.0)

    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)

    return (
        K * exp(-r * T) * norm_cdf(-d_2)
        - S * norm_cdf(-d_1)
    )
