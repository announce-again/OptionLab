from math import erf, exp, log, pi, sqrt


def norm_cdf(value: float) -> float:
    """Standard normal cumulative distribution function."""

    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def norm_pdf(value: float) -> float:
    """Standard normal probability density function."""

    return exp(-0.5 * value * value) / sqrt(2.0 * pi)


def d1(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Calculate the Black-Scholes d1 term."""

    numerator = (
        log(spot / strike)
        + (rate + 0.5 * volatility * volatility) * maturity
    )
    denominator = volatility * sqrt(maturity)

    return numerator / denominator


def d2(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Calculate the Black-Scholes d2 term."""

    return d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
    ) - volatility * sqrt(maturity)
