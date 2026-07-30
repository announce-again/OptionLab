from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import exp, isfinite
from typing import Protocol, runtime_checkable


class InterpolationPolicy(str, Enum):
    FLAT = "flat"


@runtime_checkable
class DiscountFactorCurve(Protocol):
    interpolation_policy: InterpolationPolicy

    def discount_factor(self, maturity: float) -> float:
        ...


@runtime_checkable
class ZeroRateCurve(DiscountFactorCurve, Protocol):
    def zero_rate(self, maturity: float) -> float:
        ...


@runtime_checkable
class DividendYieldCurve(DiscountFactorCurve, Protocol):
    def dividend_yield(self, maturity: float) -> float:
        ...


@dataclass(frozen=True, slots=True)
class FlatZeroRateCurve:
    rate: float
    interpolation_policy: InterpolationPolicy = InterpolationPolicy.FLAT

    def __post_init__(self) -> None:
        _validate_finite(self.rate, "rate")
        _validate_interpolation_policy(self.interpolation_policy)

    def zero_rate(self, maturity: float) -> float:
        _validate_maturity(maturity)
        return self.rate

    def discount_factor(self, maturity: float) -> float:
        _validate_maturity(maturity)
        return exp(-self.rate * maturity)


@dataclass(frozen=True, slots=True)
class FlatDividendYieldCurve:
    dividend_yield_value: float
    interpolation_policy: InterpolationPolicy = InterpolationPolicy.FLAT

    def __post_init__(self) -> None:
        _validate_finite(self.dividend_yield_value, "dividend_yield")
        _validate_interpolation_policy(self.interpolation_policy)

    def dividend_yield(self, maturity: float) -> float:
        _validate_maturity(maturity)
        return self.dividend_yield_value

    def discount_factor(self, maturity: float) -> float:
        _validate_maturity(maturity)
        return exp(-self.dividend_yield_value * maturity)


@dataclass(frozen=True, slots=True)
class CarryAssumptions:
    risk_free_curve: DiscountFactorCurve
    dividend_curve: DiscountFactorCurve

    def __post_init__(self) -> None:
        _validate_discount_factor_curve(
            self.risk_free_curve,
            "risk_free_curve",
        )
        _validate_discount_factor_curve(
            self.dividend_curve,
            "dividend_curve",
        )

    def risk_free_discount_factor(self, maturity: float) -> float:
        return self.risk_free_curve.discount_factor(maturity)

    def dividend_discount_factor(self, maturity: float) -> float:
        return self.dividend_curve.discount_factor(maturity)

    def forward_price(self, spot: float, maturity: float) -> float:
        return forward_price(
            spot=spot,
            maturity=maturity,
            risk_free_curve=self.risk_free_curve,
            dividend_curve=self.dividend_curve,
        )


def discount_factor_from_zero_rate(rate: float, maturity: float) -> float:
    _validate_finite(rate, "rate")
    _validate_maturity(maturity)
    return exp(-rate * maturity)


def forward_price(
    spot: float,
    maturity: float,
    risk_free_curve: DiscountFactorCurve,
    dividend_curve: DiscountFactorCurve,
) -> float:
    _validate_positive_finite(spot, "spot")
    _validate_maturity(maturity)
    _validate_discount_factor_curve(risk_free_curve, "risk_free_curve")
    _validate_discount_factor_curve(dividend_curve, "dividend_curve")

    risk_free_discount = risk_free_curve.discount_factor(maturity)
    dividend_discount = dividend_curve.discount_factor(maturity)
    _validate_positive_finite(risk_free_discount, "risk_free_discount_factor")
    _validate_positive_finite(dividend_discount, "dividend_discount_factor")

    return spot * dividend_discount / risk_free_discount


def flat_forward_price(
    spot: float,
    maturity: float,
    rate: float,
    dividend_yield: float,
) -> float:
    return forward_price(
        spot=spot,
        maturity=maturity,
        risk_free_curve=FlatZeroRateCurve(rate),
        dividend_curve=FlatDividendYieldCurve(dividend_yield),
    )


def _validate_maturity(maturity: float) -> None:
    _validate_finite(maturity, "maturity")
    if maturity < 0.0:
        raise ValueError("maturity must be non-negative")


def _validate_finite(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _validate_positive_finite(value: float, field_name: str) -> None:
    _validate_finite(value, field_name)
    if value <= 0.0:
        raise ValueError(f"{field_name} must be positive")


def _validate_interpolation_policy(policy: InterpolationPolicy) -> None:
    if not isinstance(policy, InterpolationPolicy):
        raise ValueError("interpolation_policy must be an InterpolationPolicy")


def _validate_discount_factor_curve(
    value: DiscountFactorCurve,
    field_name: str,
) -> None:
    if not isinstance(value, DiscountFactorCurve):
        raise ValueError(f"{field_name} must implement DiscountFactorCurve")
