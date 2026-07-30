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
    dividend_yield: float = 0.0,
) -> float:
    """Return the Black-Scholes-Merton delta of a European call."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    return exp(-dividend_yield * maturity) * norm_cdf(d_1)


def put_delta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return the Black-Scholes-Merton delta of a European put."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    return exp(-dividend_yield * maturity) * (norm_cdf(d_1) - 1.0)


def gamma(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return the Black-Scholes-Merton gamma of a European option."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    return exp(-dividend_yield * maturity) * norm_pdf(d_1) / (
        spot * volatility * sqrt(maturity)
    )


def vega(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return vega per 1.0 change in volatility."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_1 = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    return (
        spot
        * exp(-dividend_yield * maturity)
        * norm_pdf(d_1)
        * sqrt(maturity)
    )


def call_theta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return annualised market theta of a European call."""

    _validate_inputs(spot, strike, maturity, volatility)

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
    discounted_spot = spot * exp(-dividend_yield * maturity)
    discounted_strike = strike * exp(-rate * maturity)

    diffusion_decay = (
        -discounted_spot
        * norm_pdf(d_1)
        * volatility
        / (2.0 * sqrt(maturity))
    )

    discount_decay = (
        -rate * discounted_strike * norm_cdf(d_2)
    )

    dividend_effect = (
        dividend_yield * discounted_spot * norm_cdf(d_1)
    )

    return diffusion_decay + discount_decay + dividend_effect


def put_theta(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return annualised market theta of a European put."""

    _validate_inputs(spot, strike, maturity, volatility)

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
    discounted_spot = spot * exp(-dividend_yield * maturity)
    discounted_strike = strike * exp(-rate * maturity)

    diffusion_decay = (
        -discounted_spot
        * norm_pdf(d_1)
        * volatility
        / (2.0 * sqrt(maturity))
    )

    discount_effect = (
        rate * discounted_strike * norm_cdf(-d_2)
    )

    dividend_effect = (
        -dividend_yield * discounted_spot * norm_cdf(-d_1)
    )

    return diffusion_decay + discount_effect + dividend_effect


def call_rho(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return call rho per 1.0 change in interest rate."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_2 = d2(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

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
    dividend_yield: float = 0.0,
) -> float:
    """Return put rho per 1.0 change in interest rate."""

    _validate_inputs(spot, strike, maturity, volatility)

    d_2 = d2(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    return (
        -strike
        * maturity
        * exp(-rate * maturity)
        * norm_cdf(-d_2)
    )
