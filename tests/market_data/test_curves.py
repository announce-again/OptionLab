from math import exp

import pytest

from ncx_derivatives.market_data import (
    CarryAssumptions,
    FlatDividendYieldCurve,
    FlatZeroRateCurve,
    InterpolationPolicy,
    discount_factor_from_zero_rate,
    flat_forward_price,
    forward_price,
)


def test_discount_factor_from_zero_rate() -> None:
    assert discount_factor_from_zero_rate(0.05, 2.0) == pytest.approx(
        exp(-0.10),
    )
    assert discount_factor_from_zero_rate(-0.01, 1.5) == pytest.approx(
        exp(0.015),
    )


def test_flat_zero_rate_curve_discount_factor_and_rate_lookup() -> None:
    curve = FlatZeroRateCurve(0.05)

    assert curve.interpolation_policy is InterpolationPolicy.FLAT
    assert curve.zero_rate(10.0) == 0.05
    assert curve.discount_factor(2.0) == pytest.approx(exp(-0.10))


def test_flat_dividend_yield_curve_discount_factor_and_yield_lookup() -> None:
    curve = FlatDividendYieldCurve(0.02)

    assert curve.interpolation_policy is InterpolationPolicy.FLAT
    assert curve.dividend_yield(5.0) == 0.02
    assert curve.discount_factor(2.0) == pytest.approx(exp(-0.04))


def test_flat_zero_rate_discount_factor_at_zero_is_one() -> None:
    assert FlatZeroRateCurve(0.05).discount_factor(0.0) == 1.0


def test_flat_dividend_factor_at_zero_is_one() -> None:
    assert FlatDividendYieldCurve(0.02).discount_factor(0.0) == 1.0


def test_forward_price_uses_discount_factor_ratio() -> None:
    spot = 100.0
    maturity = 1.25
    risk_free = FlatZeroRateCurve(0.05)
    dividend = FlatDividendYieldCurve(0.02)

    expected = spot * exp(-0.02 * maturity) / exp(-0.05 * maturity)

    assert forward_price(spot, maturity, risk_free, dividend) == pytest.approx(
        expected,
    )


def test_flat_forward_price_matches_continuously_compounded_formula() -> None:
    spot = 100.0
    maturity = 2.0
    rate = 0.05
    dividend_yield = 0.02

    assert flat_forward_price(
        spot,
        maturity,
        rate,
        dividend_yield,
    ) == pytest.approx(spot * exp((rate - dividend_yield) * maturity))


def test_forward_at_zero_maturity_equals_spot() -> None:
    assert flat_forward_price(100.0, 0.0, 0.05, 0.02) == 100.0


def test_carry_assumptions_wrap_curve_lookups() -> None:
    carry = CarryAssumptions(
        risk_free_curve=FlatZeroRateCurve(0.05),
        dividend_curve=FlatDividendYieldCurve(0.02),
    )

    assert carry.risk_free_discount_factor(1.0) == pytest.approx(exp(-0.05))
    assert carry.dividend_discount_factor(1.0) == pytest.approx(exp(-0.02))
    assert carry.forward_price(100.0, 1.0) == pytest.approx(
        100.0 * exp(0.03),
    )


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: FlatZeroRateCurve(float("nan")), "finite"),
        (lambda: FlatDividendYieldCurve(True), "numeric"),
    ],
)
def test_curve_constructors_validate_inputs(factory, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        factory()


@pytest.mark.parametrize(
    "maturity",
    [-1.0, float("nan")],
)
def test_discount_factor_lookup_validates_maturity(maturity: float) -> None:
    curve = FlatZeroRateCurve(0.05)

    with pytest.raises(ValueError):
        curve.discount_factor(maturity)


def test_forward_price_validates_spot_and_curve_discounts() -> None:
    with pytest.raises(ValueError, match="spot"):
        flat_forward_price(0.0, 1.0, 0.05, 0.02)

    with pytest.raises(ValueError, match="maturity"):
        flat_forward_price(100.0, -1.0, 0.05, 0.02)


def test_carry_rejects_invalid_curve_objects() -> None:
    with pytest.raises(ValueError, match="risk_free_curve"):
        CarryAssumptions(
            risk_free_curve="invalid",  # type: ignore[arg-type]
            dividend_curve=FlatDividendYieldCurve(0.02),
        )

    with pytest.raises(ValueError, match="dividend_curve"):
        CarryAssumptions(
            risk_free_curve=FlatZeroRateCurve(0.05),
            dividend_curve=123,  # type: ignore[arg-type]
        )


def test_forward_price_rejects_invalid_curve_objects() -> None:
    with pytest.raises(ValueError, match="risk_free_curve"):
        forward_price(
            spot=100.0,
            maturity=1.0,
            risk_free_curve=None,  # type: ignore[arg-type]
            dividend_curve=FlatDividendYieldCurve(0.02),
        )


def test_forward_rejects_curve_returning_non_positive_factor() -> None:
    class InvalidCurve:
        interpolation_policy = InterpolationPolicy.FLAT

        def discount_factor(self, maturity: float) -> float:
            return 0.0

    with pytest.raises(ValueError, match="risk_free_discount_factor"):
        forward_price(
            spot=100.0,
            maturity=1.0,
            risk_free_curve=InvalidCurve(),
            dividend_curve=FlatDividendYieldCurve(0.02),
        )


def test_forward_rejects_curve_returning_nan() -> None:
    class InvalidCurve:
        interpolation_policy = InterpolationPolicy.FLAT

        def discount_factor(self, maturity: float) -> float:
            return float("nan")

    with pytest.raises(ValueError, match="dividend_discount_factor"):
        forward_price(
            spot=100.0,
            maturity=1.0,
            risk_free_curve=FlatZeroRateCurve(0.05),
            dividend_curve=InvalidCurve(),
        )
