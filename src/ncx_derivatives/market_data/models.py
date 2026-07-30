from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from math import isfinite


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


class ExerciseStyle(str, Enum):
    AMERICAN = "american"
    EUROPEAN = "european"
    BERMUDAN = "bermudan"


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    provider: str | None = None
    dataset: str | None = None
    schema: str | None = None
    source_record_id: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "provider",
            "dataset",
            "schema",
            "source_record_id",
        ):
            _validate_optional_text(getattr(self, field_name), field_name)


@dataclass(frozen=True, slots=True)
class ContractPairingKey:
    underlying_symbol: str
    expiration: date
    strike: float
    exercise_style: ExerciseStyle | None
    contract_multiplier: float | None
    currency: str | None

    def __post_init__(self) -> None:
        _validate_required_text(self.underlying_symbol, "underlying_symbol")
        _validate_date(self.expiration, "expiration")
        _validate_positive_finite(self.strike, "strike")
        if (
            self.exercise_style is not None
            and not isinstance(self.exercise_style, ExerciseStyle)
        ):
            raise ValueError(
                "exercise_style must be an ExerciseStyle or None",
            )
        _validate_optional_positive_finite(
            self.contract_multiplier,
            "contract_multiplier",
        )
        _validate_optional_text(self.currency, "currency")


@dataclass(frozen=True, slots=True)
class OptionContract:
    underlying_symbol: str
    expiration: date
    strike: float
    option_type: OptionType
    exercise_style: ExerciseStyle | None = None
    contract_multiplier: float | None = None
    currency: str | None = None
    source_contract_id: str | None = field(default=None, compare=False)
    display_symbol: str | None = field(default=None, compare=False)
    listing_exchange: str | None = field(default=None, compare=False)
    metadata: SourceMetadata | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        _validate_required_text(self.underlying_symbol, "underlying_symbol")
        _validate_date(self.expiration, "expiration")
        _validate_positive_finite(self.strike, "strike")
        _validate_optional_positive_finite(
            self.contract_multiplier,
            "contract_multiplier",
        )
        _validate_optional_text(self.currency, "currency")
        _validate_optional_text(self.source_contract_id, "source_contract_id")
        _validate_optional_text(self.display_symbol, "display_symbol")
        _validate_optional_text(self.listing_exchange, "listing_exchange")

        if not isinstance(self.option_type, OptionType):
            raise ValueError("option_type must be an OptionType")
        if (
            self.exercise_style is not None
            and not isinstance(self.exercise_style, ExerciseStyle)
        ):
            raise ValueError(
                "exercise_style must be an ExerciseStyle or None",
            )
        _validate_optional_metadata(self.metadata)

    @property
    def pairing_key(self) -> ContractPairingKey:
        return ContractPairingKey(
            underlying_symbol=self.underlying_symbol,
            expiration=self.expiration,
            strike=self.strike,
            exercise_style=self.exercise_style,
            contract_multiplier=self.contract_multiplier,
            currency=self.currency,
        )

    @property
    def sort_key(self) -> tuple[str, date, float, str, str, float, str]:
        return (
            self.underlying_symbol,
            self.expiration,
            self.strike,
            self.option_type.value,
            self.exercise_style.value if self.exercise_style else "",
            self.contract_multiplier if self.contract_multiplier is not None else 0.0,
            self.source_contract_id or "",
        )


@dataclass(frozen=True, slots=True)
class OptionQuote:
    contract: OptionContract
    quote_timestamp: datetime
    bid: float | None = None
    ask: float | None = None
    bid_size: int | None = None
    ask_size: int | None = None
    bid_venue: str | None = None
    ask_venue: str | None = None
    session_volume: int | None = None
    open_interest: int | None = None
    open_interest_date: date | None = None
    metadata: SourceMetadata | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.contract, OptionContract):
            raise ValueError("contract must be an OptionContract")
        _validate_aware_datetime(self.quote_timestamp, "quote_timestamp")
        _validate_optional_non_negative_finite(self.bid, "bid")
        _validate_optional_non_negative_finite(self.ask, "ask")
        _validate_optional_non_negative_int(self.bid_size, "bid_size")
        _validate_optional_non_negative_int(self.ask_size, "ask_size")
        _validate_optional_text(self.bid_venue, "bid_venue")
        _validate_optional_text(self.ask_venue, "ask_venue")
        _validate_optional_non_negative_int(
            self.session_volume,
            "session_volume",
        )
        _validate_optional_non_negative_int(
            self.open_interest,
            "open_interest",
        )
        _validate_optional_date(
            self.open_interest_date,
            "open_interest_date",
        )
        _validate_optional_metadata(self.metadata)

    @property
    def sort_key(self) -> tuple:
        return (
            self.contract.sort_key,
            self.quote_timestamp,
            self.bid is None,
            self.bid if self.bid is not None else 0.0,
            self.ask is None,
            self.ask if self.ask is not None else 0.0,
        )


@dataclass(frozen=True, slots=True)
class OptionTrade:
    contract: OptionContract
    trade_timestamp: datetime
    price: float
    size: int | None = None
    trade_venue: str | None = None
    metadata: SourceMetadata | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.contract, OptionContract):
            raise ValueError("contract must be an OptionContract")
        _validate_aware_datetime(self.trade_timestamp, "trade_timestamp")
        _validate_non_negative_finite(self.price, "price")
        _validate_optional_non_negative_int(self.size, "size")
        _validate_optional_text(self.trade_venue, "trade_venue")
        _validate_optional_metadata(self.metadata)

    @property
    def sort_key(self) -> tuple:
        return (
            self.contract.sort_key,
            self.trade_timestamp,
            self.price,
            self.size if self.size is not None else -1,
        )


@dataclass(frozen=True, slots=True)
class UnderlyingQuote:
    symbol: str
    quote_timestamp: datetime
    price: float | None = None
    bid: float | None = None
    ask: float | None = None
    bid_venue: str | None = None
    ask_venue: str | None = None
    metadata: SourceMetadata | None = None

    def __post_init__(self) -> None:
        _validate_required_text(self.symbol, "symbol")
        _validate_aware_datetime(self.quote_timestamp, "quote_timestamp")
        _validate_optional_non_negative_finite(self.price, "price")
        _validate_optional_non_negative_finite(self.bid, "bid")
        _validate_optional_non_negative_finite(self.ask, "ask")
        _validate_optional_text(self.bid_venue, "bid_venue")
        _validate_optional_text(self.ask_venue, "ask_venue")
        _validate_optional_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class OptionChainSnapshot:
    underlying_symbol: str
    as_of: datetime
    quotes: tuple[OptionQuote, ...] = field(default_factory=tuple)
    trades: tuple[OptionTrade, ...] = field(default_factory=tuple)
    underlying_quote: UnderlyingQuote | None = None
    metadata: SourceMetadata | None = None

    def __post_init__(self) -> None:
        _validate_required_text(self.underlying_symbol, "underlying_symbol")
        _validate_aware_datetime(self.as_of, "as_of")
        quotes = tuple(self.quotes)
        trades = tuple(self.trades)

        for quote in quotes:
            if not isinstance(quote, OptionQuote):
                raise ValueError("quotes must contain OptionQuote objects")

        for trade in trades:
            if not isinstance(trade, OptionTrade):
                raise ValueError("trades must contain OptionTrade objects")

        if self.underlying_quote is not None:
            if not isinstance(self.underlying_quote, UnderlyingQuote):
                raise ValueError(
                    "underlying_quote must be an UnderlyingQuote or None",
                )
            if self.underlying_quote.symbol != self.underlying_symbol:
                raise ValueError(
                    "underlying_quote symbol must match underlying_symbol",
                )

        for quote in quotes:
            if quote.contract.underlying_symbol != self.underlying_symbol:
                raise ValueError(
                    "quote contract underlying must match underlying_symbol",
                )

        for trade in trades:
            if trade.contract.underlying_symbol != self.underlying_symbol:
                raise ValueError(
                    "trade contract underlying must match underlying_symbol",
                )

        object.__setattr__(
            self,
            "quotes",
            tuple(sorted(quotes, key=lambda quote: quote.sort_key)),
        )
        object.__setattr__(
            self,
            "trades",
            tuple(sorted(trades, key=lambda trade: trade.sort_key)),
        )
        _validate_optional_metadata(self.metadata)

    @property
    def contracts(self) -> tuple[OptionContract, ...]:
        contracts = {quote.contract for quote in self.quotes}
        contracts.update(trade.contract for trade in self.trades)
        return tuple(sorted(contracts, key=lambda contract: contract.sort_key))


def _validate_required_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_optional_text(value: str | None, field_name: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ValueError(f"{field_name} must be a non-empty string or None")


def _validate_date(value: date, field_name: str) -> None:
    if not isinstance(value, date) or isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a date")


def _validate_optional_date(
    value: date | None,
    field_name: str,
) -> None:
    if value is None:
        return
    if not isinstance(value, date) or isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a date or None")


def _validate_finite(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _validate_optional_finite(
    value: float | None,
    field_name: str,
) -> None:
    if value is not None:
        _validate_finite(value, field_name)


def _validate_non_negative_finite(value: float, field_name: str) -> None:
    _validate_finite(value, field_name)
    if value < 0.0:
        raise ValueError(f"{field_name} must be non-negative")


def _validate_optional_non_negative_finite(
    value: float | None,
    field_name: str,
) -> None:
    if value is not None:
        _validate_non_negative_finite(value, field_name)


def _validate_positive_finite(value: float, field_name: str) -> None:
    _validate_finite(value, field_name)
    if value <= 0.0:
        raise ValueError(f"{field_name} must be positive")


def _validate_optional_positive_finite(
    value: float | None,
    field_name: str,
) -> None:
    if value is not None:
        _validate_positive_finite(value, field_name)


def _validate_optional_non_negative_int(
    value: int | None,
    field_name: str,
) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer or None")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _validate_aware_datetime(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _validate_optional_metadata(
    value: SourceMetadata | None,
    field_name: str = "metadata",
) -> None:
    if value is not None and not isinstance(value, SourceMetadata):
        raise ValueError(f"{field_name} must be SourceMetadata or None")
