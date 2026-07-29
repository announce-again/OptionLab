import pytest

from ncx_derivatives.greeks import (
    call_delta,
    call_rho,
    call_theta,
    gamma,
    put_delta,
    put_rho,
    put_theta,
    vega,
)


SPOT = 100.0
STRIKE = 100.0
MATURITY = 1.0
RATE = 0.05
VOLATILITY = 0.20


def test_call_delta_benchmark() -> None:
    result = call_delta(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(0.636831, abs=1e-6)


def test_put_delta_benchmark() -> None:
    result = put_delta(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(-0.363169, abs=1e-6)


def test_gamma_benchmark() -> None:
    result = gamma(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(0.018762, abs=1e-6)


def test_vega_benchmark() -> None:
    result = vega(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(37.524035, abs=1e-6)


def test_call_theta_benchmark() -> None:
    result = call_theta(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(-6.414028, abs=1e-6)


def test_put_theta_benchmark() -> None:
    result = put_theta(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(-1.657880, abs=1e-6)


def test_call_rho_benchmark() -> None:
    result = call_rho(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(53.232482, abs=1e-6)


def test_put_rho_benchmark() -> None:
    result = put_rho(
        SPOT,
        STRIKE,
        MATURITY,
        RATE,
        VOLATILITY,
    )

    assert result == pytest.approx(-41.890461, abs=1e-6)