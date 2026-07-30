from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum

from .models import (
    OptionChainSnapshot,
    OptionContract,
    OptionQuote,
    OptionTrade,
    UnderlyingQuote,
)


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class BuiltinValidationCode(str, Enum):
    CROSSED_MARKET = "CROSSED_MARKET"
    CROSSED_UNDERLYING_MARKET = "CROSSED_UNDERLYING_MARKET"
    DUPLICATE_QUOTE = "DUPLICATE_QUOTE"
    EMPTY_MARKET = "EMPTY_MARKET"
    EMPTY_SNAPSHOT = "EMPTY_SNAPSHOT"
    INCOMPLETE_UNDERLYING_MARKET = "INCOMPLETE_UNDERLYING_MARKET"
    LOCKED_MARKET = "LOCKED_MARKET"
    LOCKED_UNDERLYING_MARKET = "LOCKED_UNDERLYING_MARKET"
    MISSING_ASK = "MISSING_ASK"
    MISSING_BID = "MISSING_BID"
    MISSING_CONTRACT_MULTIPLIER = "MISSING_CONTRACT_MULTIPLIER"
    MISSING_CURRENCY = "MISSING_CURRENCY"
    MISSING_EXERCISE_STYLE = "MISSING_EXERCISE_STYLE"
    MISSING_TRADE_SIZE = "MISSING_TRADE_SIZE"
    MISSING_UNDERLYING_QUOTE = "MISSING_UNDERLYING_QUOTE"
    OPEN_INTEREST_DATE_AFTER_QUOTE = "OPEN_INTEREST_DATE_AFTER_QUOTE"
    OPEN_INTEREST_DATE_MISSING = "OPEN_INTEREST_DATE_MISSING"
    QUOTE_TIMESTAMP_AFTER_SNAPSHOT = "QUOTE_TIMESTAMP_AFTER_SNAPSHOT"
    TRADE_TIMESTAMP_AFTER_SNAPSHOT = "TRADE_TIMESTAMP_AFTER_SNAPSHOT"
    UNDERLYING_PRICE_ABOVE_ASK = "UNDERLYING_PRICE_ABOVE_ASK"
    UNDERLYING_PRICE_BELOW_BID = "UNDERLYING_PRICE_BELOW_BID"
    UNDERLYING_TIMESTAMP_AFTER_SNAPSHOT = "UNDERLYING_TIMESTAMP_AFTER_SNAPSHOT"
    ZERO_ASK = "ZERO_ASK"
    ZERO_BID = "ZERO_BID"
    ZERO_TRADE_SIZE = "ZERO_TRADE_SIZE"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: ValidationSeverity
    code: str
    message: str
    location: tuple[str, ...] = ()
    context: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.severity, ValidationSeverity):
            raise ValueError("severity must be a ValidationSeverity")
        _validate_non_empty_text(self.code, "code")
        _validate_non_empty_text(self.message, "message")

        location = tuple(self.location)
        for item in location:
            _validate_non_empty_text(item, "location item")

        context = tuple(self.context)
        for item in context:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError(
                    "context must contain key-value string pairs",
                )
            key, value = item
            _validate_non_empty_text(key, "context key")
            if not isinstance(value, str):
                raise ValueError("context values must be strings")

        object.__setattr__(self, "location", location)
        object.__setattr__(self, "context", context)

    def at(self, *prefix: str) -> ValidationIssue:
        return ValidationIssue(
            severity=self.severity,
            code=self.code,
            message=self.message,
            location=tuple(prefix) + self.location,
            context=self.context,
        )


@dataclass(frozen=True, slots=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "issues", tuple(self.issues))
        for issue in self.issues:
            if not isinstance(issue, ValidationIssue):
                raise ValueError("issues must contain ValidationIssue objects")

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return self.by_severity(ValidationSeverity.ERROR)

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return self.by_severity(ValidationSeverity.WARNING)

    @property
    def infos(self) -> tuple[ValidationIssue, ...]:
        return self.by_severity(ValidationSeverity.INFO)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

    @property
    def is_valid(self) -> bool:
        return not self.has_errors

    def by_severity(
        self,
        severity: ValidationSeverity,
    ) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity is severity)

    def by_code(self, code: str) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.code == code)

    def at_location_prefix(self, *prefix: str) -> tuple[ValidationIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if issue.location[: len(prefix)] == tuple(prefix)
        )

    def with_prefix(self, *prefix: str) -> ValidationReport:
        return ValidationReport(
            tuple(issue.at(*prefix) for issue in self.issues),
        )

    @classmethod
    def combine(cls, *reports: ValidationReport) -> ValidationReport:
        issues: list[ValidationIssue] = []
        for report in reports:
            if not isinstance(report, ValidationReport):
                raise ValueError(
                    "reports must contain ValidationReport objects",
                )
            issues.extend(report.issues)
        return cls(tuple(issues))


def validate_option_contract(contract: OptionContract) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if contract.exercise_style is None:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.MISSING_EXERCISE_STYLE.value,
                "contract exercise style is unknown",
                ("exercise_style",),
            ),
        )
    if contract.contract_multiplier is None:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.MISSING_CONTRACT_MULTIPLIER.value,
                "contract multiplier is unknown",
                ("contract_multiplier",),
            ),
        )
    if contract.currency is None:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.MISSING_CURRENCY.value,
                "contract currency is unknown",
                ("currency",),
            ),
        )

    return ValidationReport(tuple(issues))


def validate_option_quote(quote: OptionQuote) -> ValidationReport:
    issues: list[ValidationIssue] = []

    issues.extend(validate_option_contract(quote.contract).issues)

    if quote.bid is None and quote.ask is None:
        issues.append(
            _issue(
                ValidationSeverity.ERROR,
                BuiltinValidationCode.EMPTY_MARKET.value,
                "quote has neither bid nor ask",
            ),
        )
    elif quote.bid is None:
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.MISSING_BID.value,
                "quote is missing bid",
                ("bid",),
            ),
        )
    elif quote.ask is None:
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.MISSING_ASK.value,
                "quote is missing ask",
                ("ask",),
            ),
        )

    if quote.bid == 0.0:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.ZERO_BID.value,
                "quote bid is zero",
                ("bid",),
            ),
        )
    if quote.ask == 0.0:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.ZERO_ASK.value,
                "quote ask is zero",
                ("ask",),
            ),
        )

    if quote.bid is not None and quote.ask is not None:
        if quote.bid > quote.ask:
            issues.append(
                _issue(
                    ValidationSeverity.ERROR,
                    BuiltinValidationCode.CROSSED_MARKET.value,
                    "quote bid is greater than ask",
                    context=(
                        ("bid", str(quote.bid)),
                        ("ask", str(quote.ask)),
                    ),
                ),
            )
        elif quote.bid == quote.ask:
            issues.append(
                _issue(
                    ValidationSeverity.WARNING,
                    BuiltinValidationCode.LOCKED_MARKET.value,
                    "quote bid equals ask",
                    context=(
                        ("bid", str(quote.bid)),
                        ("ask", str(quote.ask)),
                    ),
                ),
            )

    if quote.open_interest is not None and quote.open_interest_date is None:
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.OPEN_INTEREST_DATE_MISSING.value,
                "open interest has no reference date",
                ("open_interest_date",),
            ),
        )
    if (
        quote.open_interest_date is not None
        and quote.open_interest_date > quote.quote_timestamp.date()
    ):
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.OPEN_INTEREST_DATE_AFTER_QUOTE.value,
                "open interest reference date is after quote timestamp",
                ("open_interest_date",),
            ),
        )

    return ValidationReport(tuple(issues))


def validate_option_trade(trade: OptionTrade) -> ValidationReport:
    issues: list[ValidationIssue] = []

    issues.extend(validate_option_contract(trade.contract).issues)
    if trade.size is None:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.MISSING_TRADE_SIZE.value,
                "trade size is unknown",
                ("size",),
            ),
        )
    elif trade.size == 0:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.ZERO_TRADE_SIZE.value,
                "trade size is zero",
                ("size",),
            ),
        )

    return ValidationReport(tuple(issues))


def validate_underlying_quote(
    underlying_quote: UnderlyingQuote,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if underlying_quote.price is None and (
        underlying_quote.bid is None or underlying_quote.ask is None
    ):
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.INCOMPLETE_UNDERLYING_MARKET.value,
                "underlying quote has no price and lacks a full bid-ask market",
            ),
        )

    if underlying_quote.bid is not None and underlying_quote.ask is not None:
        if underlying_quote.bid > underlying_quote.ask:
            issues.append(
                _issue(
                    ValidationSeverity.ERROR,
                    BuiltinValidationCode.CROSSED_UNDERLYING_MARKET.value,
                    "underlying bid is greater than ask",
                    context=(
                        ("bid", str(underlying_quote.bid)),
                        ("ask", str(underlying_quote.ask)),
                    ),
                ),
            )
        elif underlying_quote.bid == underlying_quote.ask:
            issues.append(
                _issue(
                    ValidationSeverity.WARNING,
                    BuiltinValidationCode.LOCKED_UNDERLYING_MARKET.value,
                    "underlying bid equals ask",
                    context=(
                        ("bid", str(underlying_quote.bid)),
                        ("ask", str(underlying_quote.ask)),
                    ),
                ),
            )

    if (
        underlying_quote.price is not None
        and underlying_quote.bid is not None
        and underlying_quote.price < underlying_quote.bid
    ):
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.UNDERLYING_PRICE_BELOW_BID.value,
                "underlying price is below bid",
                ("price",),
            ),
        )
    if (
        underlying_quote.price is not None
        and underlying_quote.ask is not None
        and underlying_quote.price > underlying_quote.ask
    ):
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.UNDERLYING_PRICE_ABOVE_ASK.value,
                "underlying price is above ask",
                ("price",),
            ),
        )

    return ValidationReport(tuple(issues))


def validate_option_chain_snapshot(
    snapshot: OptionChainSnapshot,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if not snapshot.quotes:
        issues.append(
            _issue(
                ValidationSeverity.WARNING,
                BuiltinValidationCode.EMPTY_SNAPSHOT.value,
                "snapshot contains no option quotes",
                ("quotes",),
            ),
        )

    if snapshot.underlying_quote is None:
        issues.append(
            _issue(
                ValidationSeverity.INFO,
                BuiltinValidationCode.MISSING_UNDERLYING_QUOTE.value,
                "snapshot has no underlying quote",
                ("underlying_quote",),
            ),
        )
    else:
        issues.extend(
            validate_underlying_quote(snapshot.underlying_quote)
            .with_prefix("underlying_quote")
            .issues,
        )
        if snapshot.underlying_quote.quote_timestamp > snapshot.as_of:
            issues.append(
                _issue(
                    ValidationSeverity.WARNING,
                    BuiltinValidationCode.UNDERLYING_TIMESTAMP_AFTER_SNAPSHOT.value,
                    "underlying quote timestamp is after snapshot timestamp",
                    ("underlying_quote", "quote_timestamp"),
                ),
            )

    quote_keys = [quote.contract for quote in snapshot.quotes]
    duplicate_quote_keys = {
        key
        for key, count in Counter(quote_keys).items()
        if count > 1
    }

    for index, quote in enumerate(snapshot.quotes):
        location = ("quotes", str(index))
        issues.extend(validate_option_quote(quote).with_prefix(*location).issues)

        if quote.quote_timestamp > snapshot.as_of:
            issues.append(
                _issue(
                    ValidationSeverity.WARNING,
                    BuiltinValidationCode.QUOTE_TIMESTAMP_AFTER_SNAPSHOT.value,
                    "quote timestamp is after snapshot timestamp",
                    location + ("quote_timestamp",),
                ),
            )
        if quote.contract in duplicate_quote_keys:
            issues.append(
                _issue(
                    ValidationSeverity.ERROR,
                    BuiltinValidationCode.DUPLICATE_QUOTE.value,
                    "duplicate quote for contract in snapshot",
                    location,
                    context=(
                        ("contract", repr(quote.contract)),
                        ("timestamp", quote.quote_timestamp.isoformat()),
                    ),
                ),
            )

    for index, trade in enumerate(snapshot.trades):
        location = ("trades", str(index))
        issues.extend(validate_option_trade(trade).with_prefix(*location).issues)

        if trade.trade_timestamp > snapshot.as_of:
            issues.append(
                _issue(
                    ValidationSeverity.WARNING,
                    BuiltinValidationCode.TRADE_TIMESTAMP_AFTER_SNAPSHOT.value,
                    "trade timestamp is after snapshot timestamp",
                    location + ("trade_timestamp",),
                ),
            )

    return ValidationReport(tuple(issues))


def _issue(
    severity: ValidationSeverity,
    code: str,
    message: str,
    location: tuple[str, ...] = (),
    context: tuple[tuple[str, str], ...] = (),
) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        code=code,
        message=message,
        location=location,
        context=context,
    )


def _validate_non_empty_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
