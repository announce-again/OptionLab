from math import exp, sqrt

from ncx_derivatives.utils.black_scholes import d1, d2, norm_cdf, norm_pdf


def _validate_inputs(
    spot: float,
    strike: float,
    maturity: float,
    volatility: float,
) -> None:
    if spot <= 0.0:
        raise ValueError("spot must be positive")

    if strike <= 0.0:
        raise ValueError("strike must be positive")

    if maturity <= 0.0:
        raise ValueError(
            "maturity must be positive when calculating Greeks"
        )

    if volatility <= 0.0:
        raise ValueError(
            "volatility must be positive when calculating Greeks"
        )


def call_delta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return the Black-Scholes delta of a European call."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(spot, strike, maturity, rate, volatility)
    return norm_cdf(d_1)


def put_delta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return the Black-Scholes delta of a European put."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(spot, strike, maturity, rate, volatility)
    return norm_cdf(d_1) - 1.0


def gamma(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return the Black-Scholes gamma of a European option."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(spot, strike, maturity, rate, volatility)

    return norm_pdf(d_1) / (
        spot * volatility * sqrt(maturity)
    )


def vega(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return vega per 1.0 change in volatility."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(spot, strike, maturity, rate, volatility)

    return spot * norm_pdf(d_1) * sqrt(maturity)


def call_theta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return annualised market theta of a European call."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(spot, strike, maturity, rate, volatility)
    d_2 = d2(spot, strike, maturity, rate, volatility)

    diffusion_decay = (
        -spot
        * norm_pdf(d_1)
        * volatility
        / (2.0 * sqrt(maturity))
    )

    discount_decay = (
        -rate
        * strike
        * exp(-rate * maturity)
        * norm_cdf(d_2)
    )

    return diffusion_decay + discount_decay


def put_theta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return annualised market theta of a European put."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(spot, strike, maturity, rate, volatility)
    d_2 = d2(spot, strike, maturity, rate, volatility)

    diffusion_decay = (
        -spot
        * norm_pdf(d_1)
        * volatility
        / (2.0 * sqrt(maturity))
    )

    discount_effect = (
        rate
        * strike
        * exp(-rate * maturity)
        * norm_cdf(-d_2)
    )

    return diffusion_decay + discount_effect


def call_rho(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return call rho per 1.0 change in interest rate."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_2 = d2(spot, strike, maturity, rate, volatility)

    return (
        strike
        * maturity
        * exp(-rate * maturity)
        * norm_cdf(d_2)
    )


def put_rho(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    """Return put rho per 1.0 change in interest rate."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_2 = d2(spot, strike, maturity, rate, volatility)

    return (
        -strike
        * maturity
        * exp(-rate * maturity)
        * norm_cdf(-d_2)
    )