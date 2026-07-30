from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite

from .derived import EnrichedOptionQuote
from .models import ContractPairingKey, ExerciseStyle, OptionType
from .validation import ValidationSeverity


class StaticArbitrageCode(str, Enum):
    PRICE_BELOW_LOWER_BOUND = "PRICE_BELOW_LOWER_BOUND"
    PRICE_ABOVE_UPPER_BOUND = "PRICE_ABOVE_UPPER_BOUND"
    CALL_PUT_PARITY_VIOLATION = "CALL_PUT_PARITY_VIOLATION"
    CALL_MONOTONICITY_VIOLATION = "CALL_MONOTONICITY_VIOLATION"
    PUT_MONOTONICITY_VIOLATION = "PUT_MONOTONICITY_VIOLATION"
    CALL_VERTICAL_SPREAD_BOUND_VIOLATION = "CALL_VERTICAL_SPREAD_BOUND_VIOLATION"
    PUT_VERTICAL_SPREAD_BOUND_VIOLATION = "PUT_VERTICAL_SPREAD_BOUND_VIOLATION"
    CONVEXITY_VIOLATION = "CONVEXITY_VIOLATION"
    BUTTERFLY_ARBITRAGE = "BUTTERFLY_ARBITRAGE"
    HEURISTIC_CALENDAR_CONSISTENCY_VIOLATION = (
        "HEURISTIC_CALENDAR_CONSISTENCY_VIOLATION"
    )


@dataclass(frozen=True, slots=True)
class StaticArbitrageConfig:
    bound_tolerance: float = 1e-8
    parity_tolerance: float = 1e-6
    monotonicity_tolerance: float = 1e-8
    vertical_spread_tolerance: float = 1e-8
    convexity_tolerance: float = 1e-8
    calendar_tolerance: float = 1e-8
    enable_single_contract_bounds: bool = True
    enable_call_put_parity: bool = True
    enable_strike_monotonicity: bool = True
    enable_vertical_spread_bounds: bool = True
    enable_convexity: bool = True
    enable_butterfly: bool = True
    enable_heuristic_calendar_consistency: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "bound_tolerance",
            "parity_tolerance",
            "monotonicity_tolerance",
            "vertical_spread_tolerance",
            "convexity_tolerance",
            "calendar_tolerance",
        ):
            _validate_non_negative_finite(getattr(self, field_name), field_name)
        for field_name in (
            "enable_single_contract_bounds",
            "enable_call_put_parity",
            "enable_strike_monotonicity",
            "enable_vertical_spread_bounds",
            "enable_convexity",
            "enable_butterfly",
            "enable_heuristic_calendar_consistency",
        ):
            _validate_bool(getattr(self, field_name), field_name)


@dataclass(frozen=True, slots=True)
class StaticArbitrageDiagnostic:
    severity: ValidationSeverity
    code: StaticArbitrageCode
    message: str
    violation_amount: float
    location: tuple[str, ...] = ()
    context: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.severity, ValidationSeverity):
            raise ValueError("severity must be a ValidationSeverity")
        if not isinstance(self.code, StaticArbitrageCode):
            raise ValueError("code must be a StaticArbitrageCode")
        _validate_non_empty_text(self.message, "message")
        _validate_non_negative_finite(self.violation_amount, "violation_amount")

        location = tuple(self.location)
        for item in location:
            _validate_non_empty_text(item, "location item")

        context = tuple(self.context)
        for item in context:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError("context must contain key-value string pairs")
            key, value = item
            _validate_non_empty_text(key, "context key")
            if not isinstance(value, str):
                raise ValueError("context values must be strings")

        object.__setattr__(self, "location", location)
        object.__setattr__(self, "context", context)


@dataclass(frozen=True, slots=True)
class StaticArbitrageReport:
    diagnostics: tuple[StaticArbitrageDiagnostic, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        diagnostics = tuple(self.diagnostics)
        for diagnostic in diagnostics:
            if not isinstance(diagnostic, StaticArbitrageDiagnostic):
                raise ValueError(
                    "diagnostics must contain StaticArbitrageDiagnostic objects",
                )
        object.__setattr__(self, "diagnostics", diagnostics)

    @property
    def has_violations(self) -> bool:
        return bool(self.diagnostics)

    @property
    def violation_count(self) -> int:
        return len(self.diagnostics)

    @property
    def max_violation_amount(self) -> float:
        if not self.diagnostics:
            return 0.0
        return max(diagnostic.violation_amount for diagnostic in self.diagnostics)

    def by_code(
        self,
        code: StaticArbitrageCode,
    ) -> tuple[StaticArbitrageDiagnostic, ...]:
        if not isinstance(code, StaticArbitrageCode):
            raise ValueError("code must be a StaticArbitrageCode")
        return tuple(diagnostic for diagnostic in self.diagnostics if diagnostic.code is code)


@dataclass(frozen=True, slots=True)
class IndexedEnrichedQuote:
    index: int
    quote: EnrichedOptionQuote

    def __post_init__(self) -> None:
        if isinstance(self.index, bool) or not isinstance(self.index, int):
            raise ValueError("index must be an integer")
        if self.index < 0:
            raise ValueError("index must be non-negative")
        if not isinstance(self.quote, EnrichedOptionQuote):
            raise ValueError("quote must be an EnrichedOptionQuote")


def diagnose_static_arbitrage(
    enriched_quotes: tuple[EnrichedOptionQuote, ...],
    config: StaticArbitrageConfig | None = None,
) -> StaticArbitrageReport:
    if config is None:
        config = StaticArbitrageConfig()
    if not isinstance(config, StaticArbitrageConfig):
        raise ValueError("config must be a StaticArbitrageConfig")

    quotes = tuple(enriched_quotes)
    for quote in quotes:
        if not isinstance(quote, EnrichedOptionQuote):
            raise ValueError("enriched_quotes must contain EnrichedOptionQuote objects")

    diagnostics: list[StaticArbitrageDiagnostic] = []
    _validate_global_valuation_state(quotes)
    priced_quotes = tuple(
        IndexedEnrichedQuote(index, quote)
        for index, quote in enumerate(quotes)
        if quote.midpoint is not None
    )

    if config.enable_single_contract_bounds:
        diagnostics.extend(_single_contract_bounds(priced_quotes, config))
    if config.enable_call_put_parity:
        diagnostics.extend(_call_put_parity(priced_quotes, config))
    if (
        config.enable_strike_monotonicity
        or config.enable_vertical_spread_bounds
        or config.enable_convexity
        or config.enable_butterfly
    ):
        diagnostics.extend(_same_expiry_strike_diagnostics(priced_quotes, config))
    if config.enable_heuristic_calendar_consistency:
        diagnostics.extend(_heuristic_calendar_consistency(priced_quotes, config))

    return StaticArbitrageReport(tuple(diagnostics))


def _single_contract_bounds(
    quotes: tuple[IndexedEnrichedQuote, ...],
    config: StaticArbitrageConfig,
) -> tuple[StaticArbitrageDiagnostic, ...]:
    diagnostics: list[StaticArbitrageDiagnostic] = []
    for item in quotes:
        index = item.index
        quote = item.quote
        if quote.no_arbitrage_bounds is None or quote.midpoint is None:
            continue
        lower_bound = quote.no_arbitrage_bounds.lower_bound
        upper_bound = quote.no_arbitrage_bounds.upper_bound
        if quote.midpoint < lower_bound - config.bound_tolerance:
            diagnostics.append(
                _diagnostic(
                    StaticArbitrageCode.PRICE_BELOW_LOWER_BOUND,
                    "option midpoint is below no-arbitrage lower bound",
                    lower_bound - quote.midpoint,
                    ("quotes", str(index)),
                    _quote_context(quote)
                    + (
                        ("midpoint", str(quote.midpoint)),
                        ("lower_bound", str(lower_bound)),
                    ),
                ),
            )
        if quote.midpoint > upper_bound + config.bound_tolerance:
            diagnostics.append(
                _diagnostic(
                    StaticArbitrageCode.PRICE_ABOVE_UPPER_BOUND,
                    "option midpoint is above no-arbitrage upper bound",
                    quote.midpoint - upper_bound,
                    ("quotes", str(index)),
                    _quote_context(quote)
                    + (
                        ("midpoint", str(quote.midpoint)),
                        ("upper_bound", str(upper_bound)),
                    ),
                ),
            )
    return tuple(diagnostics)


def _call_put_parity(
    quotes: tuple[IndexedEnrichedQuote, ...],
    config: StaticArbitrageConfig,
) -> tuple[StaticArbitrageDiagnostic, ...]:
    diagnostics: list[StaticArbitrageDiagnostic] = []
    by_pairing_key: dict[ContractPairingKey, list[IndexedEnrichedQuote]] = defaultdict(list)
    for item in quotes:
        by_pairing_key[item.quote.quote.contract.pairing_key].append(item)

    for pairing_key, items in by_pairing_key.items():
        calls = [
            item for item in items
            if item.quote.quote.contract.option_type is OptionType.CALL
        ]
        puts = [
            item for item in items
            if item.quote.quote.contract.option_type is OptionType.PUT
        ]
        if len(calls) != 1 or len(puts) != 1:
            continue
        call_item = calls[0]
        put_item = puts[0]
        call = call_item.quote
        put = put_item.quote
        if (
            call.quote.contract.exercise_style is not ExerciseStyle.EUROPEAN
            or put.quote.contract.exercise_style is not ExerciseStyle.EUROPEAN
        ):
            continue
        _validate_pair_valuation_state(call, put)
        if call.midpoint is None or put.midpoint is None:
            continue

        parity_left = call.midpoint - put.midpoint
        parity_right = call.risk_free_discount_factor * (
            call.forward_price - call.quote.contract.strike
        )
        difference = parity_left - parity_right
        violation = abs(difference)
        if violation > config.parity_tolerance:
            diagnostics.append(
                _diagnostic(
                    StaticArbitrageCode.CALL_PUT_PARITY_VIOLATION,
                    "call-put parity difference exceeds tolerance",
                    violation,
                    ("pairing_key", repr(pairing_key)),
                    (
                        ("call_index", str(call_item.index)),
                        ("put_index", str(put_item.index)),
                        ("call_midpoint", str(call.midpoint)),
                        ("put_midpoint", str(put.midpoint)),
                        ("left", str(parity_left)),
                        ("right", str(parity_right)),
                        ("difference", str(difference)),
                    ),
                ),
            )
    return tuple(diagnostics)


def _same_expiry_strike_diagnostics(
    quotes: tuple[IndexedEnrichedQuote, ...],
    config: StaticArbitrageConfig,
) -> tuple[StaticArbitrageDiagnostic, ...]:
    diagnostics: list[StaticArbitrageDiagnostic] = []
    groups: dict[tuple[tuple, object], list[IndexedEnrichedQuote]] = defaultdict(list)
    for item in quotes:
        contract = item.quote.quote.contract
        groups[
            (
                _family_key(item.quote),
                contract.expiration,
            )
        ].append(item)

    for items in groups.values():
        _validate_group_valuation_state(items)
        sorted_items = tuple(
            sorted(items, key=lambda item: item.quote.quote.contract.strike)
        )
        diagnostics.extend(_strike_pair_diagnostics(sorted_items, config))
        diagnostics.extend(_convexity_diagnostics(sorted_items, config))

    return tuple(diagnostics)


def _strike_pair_diagnostics(
    items: tuple[IndexedEnrichedQuote, ...],
    config: StaticArbitrageConfig,
) -> tuple[StaticArbitrageDiagnostic, ...]:
    diagnostics: list[StaticArbitrageDiagnostic] = []
    for left, right in zip(items, items[1:]):
        left_quote = left.quote
        right_quote = right.quote
        if left_quote.midpoint is None or right_quote.midpoint is None:
            continue
        option_type = left_quote.quote.contract.option_type
        strike_left = left_quote.quote.contract.strike
        strike_right = right_quote.quote.contract.strike
        strike_gap = strike_right - strike_left
        if strike_gap <= 0.0:
            continue

        if option_type is OptionType.CALL:
            vertical_value = left_quote.midpoint - right_quote.midpoint
            if (
                config.enable_strike_monotonicity
                and right_quote.midpoint > left_quote.midpoint + config.monotonicity_tolerance
            ):
                diagnostics.append(
                    _diagnostic(
                        StaticArbitrageCode.CALL_MONOTONICITY_VIOLATION,
                        "call price increases as strike increases",
                        right_quote.midpoint - left_quote.midpoint,
                        ("strikes", str(strike_left), str(strike_right)),
                        _pair_context(left, right),
                    ),
                )
            if (
                config.enable_vertical_spread_bounds
                and _is_european(left_quote)
                and _is_european(right_quote)
            ):
                upper_bound = left_quote.risk_free_discount_factor * strike_gap
                if vertical_value < -config.vertical_spread_tolerance:
                    diagnostics.append(
                        _diagnostic(
                            StaticArbitrageCode.CALL_VERTICAL_SPREAD_BOUND_VIOLATION,
                            "call vertical spread value is negative",
                            -vertical_value,
                            ("strikes", str(strike_left), str(strike_right)),
                            _pair_context(left, right)
                            + (("vertical_value", str(vertical_value)),),
                        ),
                    )
                elif vertical_value > upper_bound + config.vertical_spread_tolerance:
                    diagnostics.append(
                        _diagnostic(
                            StaticArbitrageCode.CALL_VERTICAL_SPREAD_BOUND_VIOLATION,
                            "call vertical spread exceeds discounted strike gap",
                            vertical_value - upper_bound,
                            ("strikes", str(strike_left), str(strike_right)),
                            _pair_context(left, right)
                            + (
                                ("vertical_value", str(vertical_value)),
                                ("upper_bound", str(upper_bound)),
                            ),
                        ),
                    )
        else:
            vertical_value = right_quote.midpoint - left_quote.midpoint
            if (
                config.enable_strike_monotonicity
                and right_quote.midpoint < left_quote.midpoint - config.monotonicity_tolerance
            ):
                diagnostics.append(
                    _diagnostic(
                        StaticArbitrageCode.PUT_MONOTONICITY_VIOLATION,
                        "put price decreases as strike increases",
                        left_quote.midpoint - right_quote.midpoint,
                        ("strikes", str(strike_left), str(strike_right)),
                        _pair_context(left, right),
                    ),
                )
            if (
                config.enable_vertical_spread_bounds
                and _is_european(left_quote)
                and _is_european(right_quote)
            ):
                upper_bound = left_quote.risk_free_discount_factor * strike_gap
                if vertical_value < -config.vertical_spread_tolerance:
                    diagnostics.append(
                        _diagnostic(
                            StaticArbitrageCode.PUT_VERTICAL_SPREAD_BOUND_VIOLATION,
                            "put vertical spread value is negative",
                            -vertical_value,
                            ("strikes", str(strike_left), str(strike_right)),
                            _pair_context(left, right)
                            + (("vertical_value", str(vertical_value)),),
                        ),
                    )
                elif vertical_value > upper_bound + config.vertical_spread_tolerance:
                    diagnostics.append(
                        _diagnostic(
                            StaticArbitrageCode.PUT_VERTICAL_SPREAD_BOUND_VIOLATION,
                            "put vertical spread exceeds discounted strike gap",
                            vertical_value - upper_bound,
                            ("strikes", str(strike_left), str(strike_right)),
                            _pair_context(left, right)
                            + (
                                ("vertical_value", str(vertical_value)),
                                ("upper_bound", str(upper_bound)),
                            ),
                        ),
                    )
    return tuple(diagnostics)


def _convexity_diagnostics(
    items: tuple[IndexedEnrichedQuote, ...],
    config: StaticArbitrageConfig,
) -> tuple[StaticArbitrageDiagnostic, ...]:
    diagnostics: list[StaticArbitrageDiagnostic] = []
    for left, middle, right in zip(items, items[1:], items[2:]):
        left_quote = left.quote
        middle_quote = middle.quote
        right_quote = right.quote
        if (
            left_quote.midpoint is None
            or middle_quote.midpoint is None
            or right_quote.midpoint is None
        ):
            continue

        strike_left = left_quote.quote.contract.strike
        strike_middle = middle_quote.quote.contract.strike
        strike_right = right_quote.quote.contract.strike
        if not strike_left < strike_middle < strike_right:
            continue

        weight = (strike_right - strike_middle) / (strike_right - strike_left)
        interpolated = weight * left_quote.midpoint + (1.0 - weight) * right_quote.midpoint
        violation = middle_quote.midpoint - interpolated
        if violation <= config.convexity_tolerance:
            continue

        context = (
            ("left_strike", str(strike_left)),
            ("middle_strike", str(strike_middle)),
            ("right_strike", str(strike_right)),
            ("left_index", str(left.index)),
            ("middle_index", str(middle.index)),
            ("right_index", str(right.index)),
            ("left_midpoint", str(left_quote.midpoint)),
            ("middle_midpoint", str(middle_quote.midpoint)),
            ("right_midpoint", str(right_quote.midpoint)),
            ("left_weight", str(weight)),
            ("right_weight", str(1.0 - weight)),
            ("linear_interpolation", str(interpolated)),
        )
        if config.enable_convexity:
            diagnostics.append(
                _diagnostic(
                    StaticArbitrageCode.CONVEXITY_VIOLATION,
                    "option price violates convexity across strikes",
                    violation,
                    ("strikes", str(strike_left), str(strike_middle), str(strike_right)),
                    context,
                ),
            )
        if config.enable_butterfly:
            diagnostics.append(
                _diagnostic(
                    StaticArbitrageCode.BUTTERFLY_ARBITRAGE,
                    "weighted butterfly convexity condition is violated",
                    violation,
                    ("strikes", str(strike_left), str(strike_middle), str(strike_right)),
                    context,
                ),
            )
    return tuple(diagnostics)


def _heuristic_calendar_consistency(
    quotes: tuple[IndexedEnrichedQuote, ...],
    config: StaticArbitrageConfig,
) -> tuple[StaticArbitrageDiagnostic, ...]:
    diagnostics: list[StaticArbitrageDiagnostic] = []
    groups: dict[tuple[tuple, float], list[IndexedEnrichedQuote]] = defaultdict(list)
    for item in quotes:
        contract = item.quote.quote.contract
        groups[
            (
                _family_key(item.quote),
                contract.strike,
            )
        ].append(item)

    for items in groups.values():
        sorted_items = tuple(sorted(items, key=lambda item: item.quote.time_to_maturity))
        for near, far in zip(sorted_items, sorted_items[1:]):
            near_quote = near.quote
            far_quote = far.quote
            if near_quote.midpoint is None or far_quote.midpoint is None:
                continue
            if far_quote.midpoint < near_quote.midpoint - config.calendar_tolerance:
                diagnostics.append(
                    _diagnostic(
                        StaticArbitrageCode.HEURISTIC_CALENDAR_CONSISTENCY_VIOLATION,
                        "heuristic raw-price calendar consistency condition is violated",
                        near_quote.midpoint - far_quote.midpoint,
                        (
                            "calendar",
                            near_quote.quote.contract.expiration.isoformat(),
                            far_quote.quote.contract.expiration.isoformat(),
                        ),
                        (
                            ("option_type", near_quote.quote.contract.option_type.value),
                            ("strike", str(near_quote.quote.contract.strike)),
                            ("near_index", str(near.index)),
                            ("far_index", str(far.index)),
                            ("near_midpoint", str(near_quote.midpoint)),
                            ("far_midpoint", str(far_quote.midpoint)),
                            ("near_maturity", str(near_quote.time_to_maturity)),
                            ("far_maturity", str(far_quote.time_to_maturity)),
                        ),
                    ),
                )
    return tuple(diagnostics)


def _diagnostic(
    code: StaticArbitrageCode,
    message: str,
    violation_amount: float,
    location: tuple[str, ...],
    context: tuple[tuple[str, str], ...] = (),
) -> StaticArbitrageDiagnostic:
    return StaticArbitrageDiagnostic(
        severity=ValidationSeverity.WARNING,
        code=code,
        message=message,
        violation_amount=violation_amount,
        location=location,
        context=context,
    )


def _quote_context(quote: EnrichedOptionQuote) -> tuple[tuple[str, str], ...]:
    contract = quote.quote.contract
    return (
        ("underlying_symbol", contract.underlying_symbol),
        ("option_type", contract.option_type.value),
        ("expiration", contract.expiration.isoformat()),
        ("strike", str(contract.strike)),
    )


def _pair_context(
    left: IndexedEnrichedQuote,
    right: IndexedEnrichedQuote,
) -> tuple[tuple[str, str], ...]:
    return (
        ("left_index", str(left.index)),
        ("right_index", str(right.index)),
        ("left_strike", str(left.quote.quote.contract.strike)),
        ("right_strike", str(right.quote.quote.contract.strike)),
        ("left_midpoint", str(left.quote.midpoint)),
        ("right_midpoint", str(right.quote.midpoint)),
    )


def _family_key(quote: EnrichedOptionQuote) -> tuple:
    contract = quote.quote.contract
    return (
        contract.underlying_symbol,
        contract.option_type,
        contract.exercise_style,
        contract.contract_multiplier,
        contract.currency,
    )


def _is_european(quote: EnrichedOptionQuote) -> bool:
    return quote.quote.contract.exercise_style is ExerciseStyle.EUROPEAN


def _validate_global_valuation_state(
    quotes: tuple[EnrichedOptionQuote, ...],
) -> None:
    if not quotes:
        return
    first = quotes[0]
    for quote in quotes[1:]:
        if quote.valuation_timestamp != first.valuation_timestamp:
            raise ValueError("all enriched quotes must share valuation_timestamp")
        if quote.valuation_date != first.valuation_date:
            raise ValueError("all enriched quotes must share valuation_date")
        if not _close(quote.spot_price, first.spot_price):
            raise ValueError("all enriched quotes must share spot_price")


def _validate_group_valuation_state(
    items: list[IndexedEnrichedQuote],
) -> None:
    if not items:
        return
    first = items[0].quote
    for item in items[1:]:
        quote = item.quote
        if not _close(quote.time_to_maturity, first.time_to_maturity):
            raise ValueError("same-expiry groups must share time_to_maturity")
        if not _close(
            quote.risk_free_discount_factor,
            first.risk_free_discount_factor,
        ):
            raise ValueError(
                "same-expiry groups must share risk_free_discount_factor",
            )
        if not _close(
            quote.dividend_discount_factor,
            first.dividend_discount_factor,
        ):
            raise ValueError(
                "same-expiry groups must share dividend_discount_factor",
            )
        if not _close(quote.forward_price, first.forward_price):
            raise ValueError("same-expiry groups must share forward_price")


def _validate_pair_valuation_state(
    call: EnrichedOptionQuote,
    put: EnrichedOptionQuote,
) -> None:
    if not _close(call.time_to_maturity, put.time_to_maturity):
        raise ValueError("call-put pairs must share time_to_maturity")
    if not _close(call.risk_free_discount_factor, put.risk_free_discount_factor):
        raise ValueError("call-put pairs must share risk_free_discount_factor")
    if not _close(call.dividend_discount_factor, put.dividend_discount_factor):
        raise ValueError("call-put pairs must share dividend_discount_factor")
    if not _close(call.forward_price, put.forward_price):
        raise ValueError("call-put pairs must share forward_price")


def _close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return abs(left - right) <= tolerance


def _validate_bool(value: bool, field_name: str) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a bool")


def _validate_non_empty_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_finite(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _validate_non_negative_finite(value: float, field_name: str) -> None:
    _validate_finite(value, field_name)
    if value < 0.0:
        raise ValueError(f"{field_name} must be non-negative")
