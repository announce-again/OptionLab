from math import erf, exp, log, sqrt


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

    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(d1, T, sigma)

    return (
        K * exp(-r * T) * _norm_cdf(-d2)
        - S * _norm_cdf(-d1)
    )