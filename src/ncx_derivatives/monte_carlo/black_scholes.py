from dataclasses import dataclass
from math import exp, sqrt
from random import Random
from statistics import NormalDist
from typing import Literal


OptionType = Literal["call", "put"]


@dataclass(frozen=True)
class MonteCarloResult:
    """Monte Carlo price estimate and sampling uncertainty."""

    price: float
    standard_error: float
    confidence_interval: tuple[float, float]
    simulations: int


def _validate_market_inputs(
    spot: float,
    strike: float,
    maturity: float,
    volatility: float,
) -> None:
    if spot <= 0.0:
        raise ValueError("spot must be positive")
    if strike <= 0.0:
        raise ValueError("strike must be positive")
    if maturity < 0.0:
        raise ValueError("maturity must be non-negative")
    if volatility < 0.0:
        raise ValueError("volatility must be non-negative")


def _validate_simulation_inputs(
    simulations: int,
    confidence_level: float,
) -> None:
    if (
        not isinstance(simulations, int)
        or isinstance(simulations, bool)
    ):
        raise ValueError("simulations must be an integer")
    if simulations <= 0:
        raise ValueError("simulations must be positive")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence level must be between 0 and 1")


def _payoff(
    option_type: OptionType,
    terminal_spot: float,
    strike: float,
) -> float:
    if option_type == "call":
        return max(terminal_spot - strike, 0.0)
    if option_type == "put":
        return max(strike - terminal_spot, 0.0)
    raise ValueError("option type must be 'call' or 'put'")


def simulate_gbm_terminal_prices(
    spot: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    *,
    simulations: int = 10_000,
    seed: int | None = None,
    antithetic: bool = False,
) -> tuple[float, ...]:
    """Simulate terminal prices under risk-neutral GBM."""

    if spot <= 0.0:
        raise ValueError("spot must be positive")
    if maturity < 0.0:
        raise ValueError("maturity must be non-negative")
    if volatility < 0.0:
        raise ValueError("volatility must be non-negative")
    _validate_simulation_inputs(simulations, 0.95)

    if maturity == 0.0:
        return tuple(spot for _ in range(simulations))

    if volatility == 0.0:
        terminal_spot = spot * exp((rate - dividend_yield) * maturity)
        return tuple(terminal_spot for _ in range(simulations))

    rng = Random(seed)
    drift = (
        rate
        - dividend_yield
        - 0.5 * volatility * volatility
    ) * maturity
    diffusion = volatility * sqrt(maturity)

    prices: list[float] = []

    if antithetic:
        pairs = simulations // 2
        for _ in range(pairs):
            shock = rng.gauss(0.0, 1.0)
            prices.append(spot * exp(drift + diffusion * shock))
            prices.append(spot * exp(drift - diffusion * shock))

        if simulations % 2:
            shock = rng.gauss(0.0, 1.0)
            prices.append(spot * exp(drift + diffusion * shock))

        return tuple(prices)

    for _ in range(simulations):
        shock = rng.gauss(0.0, 1.0)
        prices.append(spot * exp(drift + diffusion * shock))

    return tuple(prices)


def _confidence_interval(
    price: float,
    standard_error: float,
    confidence_level: float,
) -> tuple[float, float]:
    tail_probability = 0.5 + confidence_level / 2.0
    z_score = NormalDist().inv_cdf(tail_probability)
    width = z_score * standard_error
    return price - width, price + width


def _standard_error(values: tuple[float, ...]) -> float:
    count = len(values)
    if count <= 1:
        return 0.0

    mean_value = sum(values) / count
    variance = sum(
        (value - mean_value) ** 2 for value in values
    ) / (count - 1)
    return sqrt(variance / count)


def _estimator_observations(
    discounted_payoffs: tuple[float, ...],
    antithetic: bool,
) -> tuple[float, ...]:
    if not antithetic:
        return discounted_payoffs

    observations = []
    pairs = len(discounted_payoffs) // 2
    for index in range(pairs):
        first = discounted_payoffs[2 * index]
        second = discounted_payoffs[2 * index + 1]
        observations.append(0.5 * (first + second))

    if len(discounted_payoffs) % 2:
        observations.append(discounted_payoffs[-1])

    return tuple(observations)


def _apply_control_variate(
    discounted_payoffs: tuple[float, ...],
    discounted_terminal_spots: tuple[float, ...],
    expected_discounted_terminal_spot: float,
) -> tuple[float, ...]:
    payoff_mean = sum(discounted_payoffs) / len(discounted_payoffs)
    control_mean = (
        sum(discounted_terminal_spots)
        / len(discounted_terminal_spots)
    )
    control_variance = sum(
        (value - control_mean) ** 2
        for value in discounted_terminal_spots
    )

    if control_variance == 0.0:
        return discounted_payoffs

    covariance = sum(
        (payoff - payoff_mean) * (control - control_mean)
        for payoff, control in zip(
            discounted_payoffs,
            discounted_terminal_spots,
        )
    )
    beta = covariance / control_variance

    return tuple(
        payoff
        - beta
        * (control - expected_discounted_terminal_spot)
        for payoff, control in zip(
            discounted_payoffs,
            discounted_terminal_spots,
        )
    )


def _monte_carlo_price(
    option_type: OptionType,
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float,
    simulations: int,
    seed: int | None,
    confidence_level: float,
    antithetic: bool,
    control_variate: bool,
) -> MonteCarloResult:
    _validate_market_inputs(spot, strike, maturity, volatility)
    _validate_simulation_inputs(simulations, confidence_level)

    terminal_prices = simulate_gbm_terminal_prices(
        spot,
        maturity,
        rate,
        volatility,
        dividend_yield,
        simulations=simulations,
        seed=seed,
        antithetic=antithetic,
    )
    discount_factor = exp(-rate * maturity)
    discounted_payoffs = tuple(
        discount_factor * _payoff(option_type, terminal_spot, strike)
        for terminal_spot in terminal_prices
    )

    if control_variate:
        discounted_terminal_spots = tuple(
            discount_factor * terminal_spot
            for terminal_spot in terminal_prices
        )
        expected_discounted_terminal_spot = (
            spot * exp(-dividend_yield * maturity)
        )
        discounted_payoffs = _apply_control_variate(
            discounted_payoffs,
            discounted_terminal_spots,
            expected_discounted_terminal_spot,
        )

    estimator_observations = _estimator_observations(
        discounted_payoffs,
        antithetic,
    )
    price = sum(estimator_observations) / len(estimator_observations)
    standard_error = _standard_error(estimator_observations)

    return MonteCarloResult(
        price=price,
        standard_error=standard_error,
        confidence_interval=_confidence_interval(
            price,
            standard_error,
            confidence_level,
        ),
        simulations=simulations,
    )


def monte_carlo_call_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    *,
    simulations: int = 10_000,
    seed: int | None = None,
    confidence_level: float = 0.95,
    antithetic: bool = False,
    control_variate: bool = False,
) -> MonteCarloResult:
    """Estimate a European call price under Black-Scholes-Merton."""

    return _monte_carlo_price(
        "call",
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        simulations,
        seed,
        confidence_level,
        antithetic,
        control_variate,
    )


def monte_carlo_put_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    *,
    simulations: int = 10_000,
    seed: int | None = None,
    confidence_level: float = 0.95,
    antithetic: bool = False,
    control_variate: bool = False,
) -> MonteCarloResult:
    """Estimate a European put price under Black-Scholes-Merton."""

    return _monte_carlo_price(
        "put",
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        simulations,
        seed,
        confidence_level,
        antithetic,
        control_variate,
    )
