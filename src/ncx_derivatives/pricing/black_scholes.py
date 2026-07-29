from math import erf, exp, log, sqrt


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


def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _d1(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
) -> float:
    return (
        log(S / K)
        + (r + 0.5 * sigma ** 2) * T
    ) / (sigma * sqrt(T))


def _d2(
    d1: float,
    T: float,
    sigma: float,
) -> float:
    return d1 - sigma * sqrt(T)


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

    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(d1, T, sigma)

    return (
        S * _norm_cdf(d1)
        - K * exp(-r * T) * _norm_cdf(d2)
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

    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(d1, T, sigma)

    return (
        K * exp(-r * T) * _norm_cdf(-d2)
        - S * _norm_cdf(-d1)
    )
