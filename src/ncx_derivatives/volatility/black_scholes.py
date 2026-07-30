from collections.abc import Callable
from math import exp, inf, pi, sqrt

from ncx_derivatives.greeks import vega
from ncx_derivatives.pricing import call_price, put_price


PriceFunction = Callable[[float, float, float, float, float, float], float]


def _validate_inputs(
    option_price: float,
    spot: float,
    strike: float,
    maturity: float,
) -> None:
    if option_price < 0.0:
        raise ValueError("option price must be non-negative")
    if spot <= 0.0:
        raise ValueError("spot must be positive")
    if strike <= 0.0:
        raise ValueError("strike must be positive")
    if maturity < 0.0:
        raise ValueError("maturity must be non-negative")


def _no_arbitrage_bounds(
    option_type: str,
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    dividend_yield: float,
) -> tuple[float, float]:
    if maturity == 0.0:
        payoff = (
            max(spot - strike, 0.0)
            if option_type == "call"
            else max(strike - spot, 0.0)
        )
        return payoff, payoff

    discounted_strike = strike * exp(-rate * maturity)
    discounted_spot = spot * exp(-dividend_yield * maturity)

    if option_type == "call":
        return max(discounted_spot - discounted_strike, 0.0), discounted_spot

    return max(discounted_strike - discounted_spot, 0.0), discounted_strike


def _validate_price_bounds(
    option_price: float,
    lower_bound: float,
    upper_bound: float,
    tolerance: float,
) -> None:
    if option_price < lower_bound - tolerance:
        raise ValueError("option price is below no-arbitrage lower bound")
    if option_price > upper_bound + tolerance:
        raise ValueError("option price is above no-arbitrage upper bound")


def _initial_volatility_guess(
    option_price: float,
    lower_bound: float,
    spot: float,
    maturity: float,
) -> float:
    extrinsic_value = max(option_price - lower_bound, 0.0)
    if extrinsic_value == 0.0:
        return 0.20

    guess = sqrt(2.0 * pi / maturity) * (extrinsic_value / spot)
    return min(max(guess, 1e-6), 5.0)


def _implied_volatility(
    option_price: float,
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    dividend_yield: float,
    price_function: PriceFunction,
    option_type: str,
    *,
    price_tolerance: float = 1e-10,
    volatility_tolerance: float = 1e-10,
    max_iterations: int = 100,
    max_volatility: float = 10.0,
    use_newton: bool = True,
) -> float:
    _validate_inputs(option_price, spot, strike, maturity)

    lower_bound, upper_bound = _no_arbitrage_bounds(
        option_type,
        spot,
        strike,
        maturity,
        rate,
        dividend_yield,
    )
    _validate_price_bounds(
        option_price,
        lower_bound,
        upper_bound,
        price_tolerance,
    )

    if option_price <= lower_bound + price_tolerance:
        return 0.0
    if maturity == 0.0:
        return 0.0
    if option_price >= upper_bound - price_tolerance:
        return inf

    low = 0.0
    high = 1.0

    while high < max_volatility:
        if (
            price_function(
                spot,
                strike,
                maturity,
                rate,
                high,
                dividend_yield,
            )
            >= option_price
        ):
            break
        high *= 2.0
    else:
        high = max_volatility

    if (
        price_function(
            spot,
            strike,
            maturity,
            rate,
            high,
            dividend_yield,
        )
        < option_price
    ):
        raise ValueError("implied volatility exceeds solver upper bound")

    sigma = _initial_volatility_guess(
        option_price,
        lower_bound,
        spot,
        maturity,
    )
    sigma = min(max(sigma, low), high)

    for _ in range(max_iterations):
        model_price = price_function(
            spot,
            strike,
            maturity,
            rate,
            sigma,
            dividend_yield,
        )
        price_error = model_price - option_price

        if abs(price_error) <= price_tolerance:
            return sigma

        if price_error > 0.0:
            high = sigma
        else:
            low = sigma

        if high - low <= volatility_tolerance:
            return 0.5 * (low + high)

        next_sigma = 0.5 * (low + high)

        if use_newton and sigma > 0.0:
            option_vega = vega(
                spot,
                strike,
                maturity,
                rate,
                sigma,
                dividend_yield,
            )
            if option_vega > 1e-12:
                newton_sigma = sigma - price_error / option_vega
                if low < newton_sigma < high:
                    next_sigma = newton_sigma

        sigma = next_sigma

    return 0.5 * (low + high)


def call_implied_volatility(
    option_price: float,
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return Black-Scholes-Merton implied volatility for a European call."""

    return _implied_volatility(
        option_price,
        spot,
        strike,
        maturity,
        rate,
        dividend_yield,
        call_price,
        "call",
    )


def put_implied_volatility(
    option_price: float,
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return Black-Scholes-Merton implied volatility for a European put."""

    return _implied_volatility(
        option_price,
        spot,
        strike,
        maturity,
        rate,
        dividend_yield,
        put_price,
        "put",
    )
