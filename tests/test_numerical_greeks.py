import pytest

from ncx_derivatives.greeks import (
    NumericalGreekResult,
    call_delta,
    call_rho,
    call_theta,
    gamma,
    numerical_delta,
    numerical_gamma,
    numerical_rho,
    numerical_theta,
    numerical_vega,
    vega,
)
from ncx_derivatives.monte_carlo import monte_carlo_call_price
from ncx_derivatives.pricing import binomial_call_price, call_price


@pytest.mark.parametrize(
    ("spot", "strike", "maturity", "rate", "volatility", "dividend_yield"),
    [
        (100.0, 100.0, 1.0, 0.05, 0.20, 0.02),
        (120.0, 100.0, 0.50, 0.03, 0.30, 0.01),
        (80.0, 100.0, 2.00, -0.01, 0.40, 0.04),
    ],
)
def test_numerical_greeks_match_analytical_black_scholes_merton(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float,
) -> None:
    assert numerical_delta(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    ) == pytest.approx(
        call_delta(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            dividend_yield,
        ),
        rel=1e-6,
        abs=1e-8,
    )
    assert numerical_gamma(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    ) == pytest.approx(
        gamma(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            dividend_yield,
        ),
        rel=1e-5,
        abs=1e-8,
    )
    assert numerical_vega(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        bump=1e-5,
    ) == pytest.approx(
        vega(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            dividend_yield,
        ),
        rel=1e-6,
        abs=1e-7,
    )
    assert numerical_theta(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        bump=1e-5,
    ) == pytest.approx(
        call_theta(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            dividend_yield,
        ),
        rel=1e-6,
        abs=1e-7,
    )
    assert numerical_rho(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        bump=1e-5,
    ) == pytest.approx(
        call_rho(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            dividend_yield,
        ),
        rel=1e-6,
        abs=1e-7,
    )


@pytest.mark.parametrize("method", ["central", "forward", "backward"])
def test_numerical_delta_supports_difference_methods(method: str) -> None:
    result = numerical_delta(
        call_price,
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        method=method,
        bump=1e-3,
        return_diagnostics=True,
    )

    assert isinstance(result, NumericalGreekResult)
    assert result.method == method
    assert result.parameter == "spot"
    assert result.evaluations == 2
    assert result.value == pytest.approx(
        call_delta(100.0, 100.0, 1.0, 0.05, 0.20),
        rel=2e-4,
    )


def test_numerical_gamma_returns_diagnostics() -> None:
    result = numerical_gamma(
        call_price,
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        return_diagnostics=True,
    )

    assert isinstance(result, NumericalGreekResult)
    assert result.parameter == "spot"
    assert result.method == "central"
    assert result.evaluations == 3
    assert len(result.prices) == 3


def test_numerical_delta_works_with_binomial_pricer() -> None:
    result = numerical_delta(
        binomial_call_price,
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        0.02,
        bump=0.50,
        steps=800,
    )

    assert result == pytest.approx(
        call_delta(100.0, 100.0, 1.0, 0.05, 0.20, 0.02),
        abs=2e-2,
    )


def test_numerical_delta_works_with_monte_carlo_result_and_common_seed() -> None:
    result = numerical_delta(
        monte_carlo_call_price,
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        0.02,
        bump=0.10,
        simulations=40_000,
        seed=123,
        control_variate=True,
    )

    assert result == pytest.approx(
        call_delta(100.0, 100.0, 1.0, 0.05, 0.20, 0.02),
        abs=3e-2,
    )


def test_common_random_numbers_reduce_monte_carlo_delta_noise() -> None:
    common_seed_delta = numerical_delta(
        monte_carlo_call_price,
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        0.02,
        bump=0.10,
        simulations=20_000,
        seed=99,
    )

    def independent_seed_call(
        spot: float,
        strike: float,
        maturity: float,
        rate: float,
        volatility: float,
        dividend_yield: float = 0.0,
        **kwargs,
    ):
        seed = 101 if spot < 100.0 else 202
        return monte_carlo_call_price(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            dividend_yield,
            seed=seed,
            **kwargs,
        )

    independent_seed_delta = numerical_delta(
        independent_seed_call,
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        0.02,
        bump=0.10,
        simulations=20_000,
    )
    analytical_delta = call_delta(
        100.0,
        100.0,
        1.0,
        0.05,
        0.20,
        0.02,
    )

    assert abs(common_seed_delta - analytical_delta) < abs(
        independent_seed_delta - analytical_delta
    )


@pytest.mark.parametrize("method", ["bad", ""])
def test_numerical_greeks_reject_invalid_method(method: str) -> None:
    with pytest.raises(ValueError):
        numerical_delta(
            call_price,
            100.0,
            100.0,
            1.0,
            0.05,
            0.20,
            method=method,
        )


@pytest.mark.parametrize("bump", [0.0, -1e-4])
def test_numerical_greeks_reject_invalid_bump(bump: float) -> None:
    with pytest.raises(ValueError):
        numerical_vega(
            call_price,
            100.0,
            100.0,
            1.0,
            0.05,
            0.20,
            bump=bump,
        )


def test_numerical_greeks_reject_bump_crossing_zero() -> None:
    with pytest.raises(ValueError):
        numerical_theta(
            call_price,
            100.0,
            100.0,
            0.01,
            0.05,
            0.20,
            bump=0.02,
        )


def test_numerical_greeks_allow_forward_bump_from_zero_maturity() -> None:
    result = numerical_theta(
        call_price,
        100.0,
        100.0,
        0.0,
        0.05,
        0.20,
        bump=1e-4,
        method="forward",
    )

    assert result <= 0.0


def test_numerical_greeks_allow_forward_bump_from_zero_volatility() -> None:
    result = numerical_vega(
        call_price,
        100.0,
        100.0,
        1.0,
        0.05,
        0.0,
        bump=1e-4,
        method="forward",
    )

    assert result >= 0.0


def test_numerical_greeks_reject_bool_price_return() -> None:
    def bool_pricer(*args, **kwargs) -> bool:
        return True

    with pytest.raises(TypeError):
        numerical_delta(
            bool_pricer,
            100.0,
            100.0,
            1.0,
            0.05,
            0.20,
        )


def test_numerical_greeks_reject_bool_price_attribute() -> None:
    class BoolPrice:
        price = True

    def bool_price_pricer(*args, **kwargs) -> BoolPrice:
        return BoolPrice()

    with pytest.raises(TypeError):
        numerical_delta(
            bool_price_pricer,
            100.0,
            100.0,
            1.0,
            0.05,
            0.20,
        )
