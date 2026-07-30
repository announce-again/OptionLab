from __future__ import annotations

from datetime import date, datetime
from math import isfinite
from typing import Any, Iterable, Mapping

from .cleaning import CleaningResult, EnrichedCleaningResult
from .derived import EnrichedOptionQuote
from .models import (
    ExerciseStyle,
    OptionChainSnapshot,
    OptionContract,
    OptionQuote,
    OptionType,
    SourceMetadata,
    UnderlyingQuote,
)
from .static_arbitrage import StaticArbitrageReport
from .validation import ValidationReport


OPTION_CHAIN_COLUMNS = (
    "underlying_symbol",
    "snapshot_as_of",
    "snapshot_provider",
    "snapshot_dataset",
    "snapshot_schema",
    "snapshot_source_record_id",
    "quote_timestamp",
    "expiration",
    "strike",
    "option_type",
    "exercise_style",
    "contract_multiplier",
    "currency",
    "source_contract_id",
    "display_symbol",
    "listing_exchange",
    "contract_provider",
    "contract_dataset",
    "contract_schema",
    "contract_source_record_id",
    "bid",
    "ask",
    "bid_size",
    "ask_size",
    "bid_venue",
    "ask_venue",
    "session_volume",
    "open_interest",
    "open_interest_date",
    "quote_provider",
    "quote_dataset",
    "quote_schema",
    "quote_source_record_id",
    "underlying_quote_timestamp",
    "underlying_price",
    "underlying_bid",
    "underlying_ask",
    "underlying_bid_venue",
    "underlying_ask_venue",
)

ENRICHED_QUOTE_COLUMNS = ("underlying_symbol",) + OPTION_CHAIN_COLUMNS[6:33] + (
    "valuation_timestamp",
    "valuation_date",
    "midpoint",
    "absolute_spread",
    "relative_spread",
    "time_to_maturity",
    "risk_free_discount_factor",
    "dividend_discount_factor",
    "forward_price",
    "spot_price",
    "spot_moneyness",
    "forward_moneyness",
    "log_moneyness",
    "intrinsic_value",
    "time_value",
    "lower_bound",
    "upper_bound",
)

VALIDATION_REPORT_COLUMNS = (
    "severity",
    "code",
    "message",
    "location",
    "context",
)

CLEANING_DIAGNOSTIC_COLUMNS = (
    "underlying_symbol",
    "expiration",
    "strike",
    "option_type",
    "reason",
    "severity",
    "message",
    "location",
    "context",
)

STATIC_ARBITRAGE_COLUMNS = (
    "severity",
    "code",
    "message",
    "violation_amount",
    "location",
    "context",
)


def option_chain_to_records(
    snapshot: OptionChainSnapshot,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(snapshot, OptionChainSnapshot):
        raise ValueError("snapshot must be an OptionChainSnapshot")
    return tuple(_quote_record(snapshot, quote) for quote in snapshot.quotes)


def option_chain_from_records(
    records: Iterable[Mapping[str, Any]],
) -> OptionChainSnapshot:
    rows = tuple(records)
    if not rows:
        raise ValueError("records must not be empty")
    _validate_record_rows(rows)

    underlying_symbols = {_required_text(row, "underlying_symbol") for row in rows}
    if len(underlying_symbols) != 1:
        raise ValueError("records must contain one underlying_symbol")
    snapshot_times = {_required_datetime(row, "snapshot_as_of") for row in rows}
    if len(snapshot_times) != 1:
        raise ValueError("records must contain one snapshot_as_of")

    snapshot_metadata = _consistent_snapshot_metadata(rows)
    underlying_quote = _consistent_underlying_quote(rows)
    quotes = tuple(_quote_from_record(row) for row in rows)
    return OptionChainSnapshot(
        underlying_symbol=underlying_symbols.pop(),
        as_of=snapshot_times.pop(),
        quotes=quotes,
        underlying_quote=underlying_quote,
        metadata=snapshot_metadata,
    )


def option_chain_to_dataframe(snapshot: OptionChainSnapshot):
    pandas = _import_pandas()
    return pandas.DataFrame.from_records(
        option_chain_to_records(snapshot),
        columns=OPTION_CHAIN_COLUMNS,
    )


def option_chain_from_dataframe(frame) -> OptionChainSnapshot:
    _validate_dataframe(frame)
    return option_chain_from_records(_dataframe_to_records(frame))


def enriched_quotes_to_records(
    enriched_quotes: Iterable[EnrichedOptionQuote],
) -> tuple[dict[str, Any], ...]:
    items = tuple(enriched_quotes)
    for item in items:
        if not isinstance(item, EnrichedOptionQuote):
            raise ValueError(
                "enriched_quotes must contain EnrichedOptionQuote objects",
            )
    return tuple(_enriched_record(item) for item in items)


def enriched_quotes_to_dataframe(enriched_quotes: Iterable[EnrichedOptionQuote]):
    pandas = _import_pandas()
    return pandas.DataFrame.from_records(
        enriched_quotes_to_records(enriched_quotes),
        columns=ENRICHED_QUOTE_COLUMNS,
    )


def validation_report_to_records(
    report: ValidationReport,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(report, ValidationReport):
        raise ValueError("report must be a ValidationReport")
    return tuple(
        {
            "severity": issue.severity.value,
            "code": issue.code,
            "message": issue.message,
            "location": "/".join(issue.location),
            "context": dict(issue.context),
        }
        for issue in report.issues
    )


def validation_report_to_dataframe(report: ValidationReport):
    pandas = _import_pandas()
    return pandas.DataFrame.from_records(
        validation_report_to_records(report),
        columns=VALIDATION_REPORT_COLUMNS,
    )


def cleaning_result_to_records(
    result: CleaningResult | EnrichedCleaningResult,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(result, (CleaningResult, EnrichedCleaningResult)):
        raise ValueError("result must be a CleaningResult or EnrichedCleaningResult")

    records: list[dict[str, Any]] = []
    for rejected in result.rejected:
        contract = rejected.quote.contract
        for diagnostic in rejected.diagnostics:
            records.append(
                {
                    "underlying_symbol": contract.underlying_symbol,
                    "expiration": contract.expiration,
                    "strike": contract.strike,
                    "option_type": contract.option_type.value,
                    "reason": diagnostic.reason.value,
                    "severity": diagnostic.severity.value,
                    "message": diagnostic.message,
                    "location": "/".join(diagnostic.location),
                    "context": dict(diagnostic.context),
                },
            )
    return tuple(records)


def cleaning_result_to_dataframe(result: CleaningResult | EnrichedCleaningResult):
    pandas = _import_pandas()
    return pandas.DataFrame.from_records(
        cleaning_result_to_records(result),
        columns=CLEANING_DIAGNOSTIC_COLUMNS,
    )


def static_arbitrage_report_to_records(
    report: StaticArbitrageReport,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(report, StaticArbitrageReport):
        raise ValueError("report must be a StaticArbitrageReport")
    return tuple(
        {
            "severity": diagnostic.severity.value,
            "code": diagnostic.code.value,
            "message": diagnostic.message,
            "violation_amount": diagnostic.violation_amount,
            "location": "/".join(diagnostic.location),
            "context": dict(diagnostic.context),
        }
        for diagnostic in report.diagnostics
    )


def static_arbitrage_report_to_dataframe(report: StaticArbitrageReport):
    pandas = _import_pandas()
    return pandas.DataFrame.from_records(
        static_arbitrage_report_to_records(report),
        columns=STATIC_ARBITRAGE_COLUMNS,
    )


def _quote_record(
    snapshot: OptionChainSnapshot,
    quote: OptionQuote,
) -> dict[str, Any]:
    contract = quote.contract
    underlying = snapshot.underlying_quote
    return {
        "underlying_symbol": snapshot.underlying_symbol,
        "snapshot_as_of": snapshot.as_of,
        "snapshot_provider": _metadata_value(snapshot.metadata, "provider"),
        "snapshot_dataset": _metadata_value(snapshot.metadata, "dataset"),
        "snapshot_schema": _metadata_value(snapshot.metadata, "schema"),
        "snapshot_source_record_id": _metadata_value(
            snapshot.metadata,
            "source_record_id",
        ),
        **_option_quote_record(quote),
        "underlying_quote_timestamp": (
            None if underlying is None else underlying.quote_timestamp
        ),
        "underlying_price": None if underlying is None else underlying.price,
        "underlying_bid": None if underlying is None else underlying.bid,
        "underlying_ask": None if underlying is None else underlying.ask,
        "underlying_bid_venue": None if underlying is None else underlying.bid_venue,
        "underlying_ask_venue": None if underlying is None else underlying.ask_venue,
    }


def _enriched_record(item: EnrichedOptionQuote) -> dict[str, Any]:
    bounds = item.no_arbitrage_bounds
    return {
        **_option_quote_record(item.quote),
        "valuation_timestamp": item.valuation_timestamp,
        "valuation_date": item.valuation_date,
        "midpoint": item.midpoint,
        "absolute_spread": item.absolute_spread,
        "relative_spread": item.relative_spread,
        "time_to_maturity": item.time_to_maturity,
        "risk_free_discount_factor": item.risk_free_discount_factor,
        "dividend_discount_factor": item.dividend_discount_factor,
        "forward_price": item.forward_price,
        "spot_price": item.spot_price,
        "spot_moneyness": item.spot_moneyness,
        "forward_moneyness": item.forward_moneyness,
        "log_moneyness": item.log_moneyness,
        "intrinsic_value": item.intrinsic_value,
        "time_value": item.time_value,
        "lower_bound": None if bounds is None else bounds.lower_bound,
        "upper_bound": None if bounds is None else bounds.upper_bound,
    }


def _option_quote_record(quote: OptionQuote) -> dict[str, Any]:
    contract = quote.contract
    return {
        "underlying_symbol": contract.underlying_symbol,
        "quote_timestamp": quote.quote_timestamp,
        "expiration": contract.expiration,
        "strike": contract.strike,
        "option_type": contract.option_type.value,
        "exercise_style": _enum_value(contract.exercise_style),
        "contract_multiplier": contract.contract_multiplier,
        "currency": contract.currency,
        "source_contract_id": contract.source_contract_id,
        "display_symbol": contract.display_symbol,
        "listing_exchange": contract.listing_exchange,
        "contract_provider": _metadata_value(contract.metadata, "provider"),
        "contract_dataset": _metadata_value(contract.metadata, "dataset"),
        "contract_schema": _metadata_value(contract.metadata, "schema"),
        "contract_source_record_id": _metadata_value(
            contract.metadata,
            "source_record_id",
        ),
        "bid": quote.bid,
        "ask": quote.ask,
        "bid_size": quote.bid_size,
        "ask_size": quote.ask_size,
        "bid_venue": quote.bid_venue,
        "ask_venue": quote.ask_venue,
        "session_volume": quote.session_volume,
        "open_interest": quote.open_interest,
        "open_interest_date": quote.open_interest_date,
        "quote_provider": _metadata_value(quote.metadata, "provider"),
        "quote_dataset": _metadata_value(quote.metadata, "dataset"),
        "quote_schema": _metadata_value(quote.metadata, "schema"),
        "quote_source_record_id": _metadata_value(
            quote.metadata,
            "source_record_id",
        ),
    }


def _quote_from_record(row: Mapping[str, Any]) -> OptionQuote:
    contract = OptionContract(
        underlying_symbol=_required_text(row, "underlying_symbol"),
        expiration=_required_date(row, "expiration"),
        strike=_required_float(row, "strike"),
        option_type=OptionType(_required_text(row, "option_type")),
        exercise_style=_optional_exercise_style(row.get("exercise_style")),
        contract_multiplier=_optional_float(row.get("contract_multiplier")),
        currency=_optional_text(row.get("currency")),
        source_contract_id=_optional_text(row.get("source_contract_id")),
        display_symbol=_optional_text(row.get("display_symbol")),
        listing_exchange=_optional_text(row.get("listing_exchange")),
        metadata=_source_metadata_from_prefix(row, "contract"),
    )
    return OptionQuote(
        contract=contract,
        quote_timestamp=_required_datetime(row, "quote_timestamp"),
        bid=_optional_float(row.get("bid")),
        ask=_optional_float(row.get("ask")),
        bid_size=_optional_int(row.get("bid_size")),
        ask_size=_optional_int(row.get("ask_size")),
        bid_venue=_optional_text(row.get("bid_venue")),
        ask_venue=_optional_text(row.get("ask_venue")),
        session_volume=_optional_int(row.get("session_volume")),
        open_interest=_optional_int(row.get("open_interest")),
        open_interest_date=_optional_date(row.get("open_interest_date")),
        metadata=_source_metadata_from_prefix(row, "quote"),
    )


def _underlying_quote_from_record(row: Mapping[str, Any]) -> UnderlyingQuote | None:
    timestamp = _optional_datetime(row.get("underlying_quote_timestamp"))
    price = _optional_float(row.get("underlying_price"))
    bid = _optional_float(row.get("underlying_bid"))
    ask = _optional_float(row.get("underlying_ask"))
    if timestamp is None and price is None and bid is None and ask is None:
        return None
    if timestamp is None:
        raise ValueError("underlying_quote_timestamp is required for underlying data")
    return UnderlyingQuote(
        symbol=_required_text(row, "underlying_symbol"),
        quote_timestamp=timestamp,
        price=price,
        bid=bid,
        ask=ask,
        bid_venue=_optional_text(row.get("underlying_bid_venue")),
        ask_venue=_optional_text(row.get("underlying_ask_venue")),
    )


def _validate_record_rows(rows: tuple[Mapping[str, Any], ...]) -> None:
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("records must contain mapping objects")


def _consistent_snapshot_metadata(
    rows: tuple[Mapping[str, Any], ...],
) -> SourceMetadata | None:
    metadata = tuple(_source_metadata_from_prefix(row, "snapshot") for row in rows)
    first = metadata[0]
    if any(item != first for item in metadata[1:]):
        raise ValueError("records must contain consistent snapshot metadata")
    return first


def _consistent_underlying_quote(
    rows: tuple[Mapping[str, Any], ...],
) -> UnderlyingQuote | None:
    underlying_quotes = tuple(_underlying_quote_from_record(row) for row in rows)
    first = underlying_quotes[0]
    if any(item != first for item in underlying_quotes[1:]):
        raise ValueError("records must contain consistent underlying quote data")
    return first


def _source_metadata_from_prefix(
    row: Mapping[str, Any],
    prefix: str,
) -> SourceMetadata | None:
    metadata = SourceMetadata(
        provider=_optional_text(row.get(f"{prefix}_provider")),
        dataset=_optional_text(row.get(f"{prefix}_dataset")),
        schema=_optional_text(row.get(f"{prefix}_schema")),
        source_record_id=_optional_text(row.get(f"{prefix}_source_record_id")),
    )
    if (
        metadata.provider is None
        and metadata.dataset is None
        and metadata.schema is None
        and metadata.source_record_id is None
    ):
        return None
    return metadata


def _metadata_value(metadata: SourceMetadata | None, field_name: str) -> str | None:
    if metadata is None:
        return None
    return getattr(metadata, field_name)


def _enum_value(value) -> str | None:
    return None if value is None else value.value


def _required_text(row: Mapping[str, Any], field_name: str) -> str:
    value = row.get(field_name)
    if _is_missing(value) or not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _optional_text(value: Any) -> str | None:
    if _is_missing(value):
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("optional text fields must be strings or missing")
    return value


def _required_float(row: Mapping[str, Any], field_name: str) -> float:
    value = _optional_float(row.get(field_name))
    if value is None:
        raise ValueError(f"{field_name} is required")
    return value


def _optional_float(value: Any) -> float | None:
    if _is_missing(value):
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("numeric fields must be numbers or missing")
    result = float(value)
    if not isfinite(result):
        raise ValueError("numeric fields must be finite or missing")
    return result


def _optional_int(value: Any) -> int | None:
    if _is_missing(value):
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("integer fields must be numbers or missing")
    if not isfinite(float(value)):
        raise ValueError("integer fields must be finite or missing")
    if int(value) != value:
        raise ValueError("integer fields must be integral")
    return int(value)


def _required_datetime(row: Mapping[str, Any], field_name: str) -> datetime:
    value = _optional_datetime(row.get(field_name))
    if value is None:
        raise ValueError(f"{field_name} is required")
    return value


def _optional_datetime(value: Any) -> datetime | None:
    if _is_missing(value):
        return None
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if not isinstance(value, datetime):
        raise ValueError("datetime fields must be datetimes or missing")
    return value


def _required_date(row: Mapping[str, Any], field_name: str) -> date:
    value = _optional_date(row.get(field_name))
    if value is None:
        raise ValueError(f"{field_name} is required")
    return value


def _optional_date(value: Any) -> date | None:
    if _is_missing(value):
        return None
    if hasattr(value, "date") and not isinstance(value, date):
        value = value.date()
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, date):
        raise ValueError("date fields must be dates or missing")
    return value


def _optional_exercise_style(value: Any) -> ExerciseStyle | None:
    text = _optional_text(value)
    if text is None:
        return None
    return ExerciseStyle(text)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if value != value:
            return True
    except TypeError:
        pass
    return False


def _validate_dataframe(frame) -> None:
    pandas = _import_pandas()
    if not isinstance(frame, pandas.DataFrame):
        raise ValueError("frame must be a pandas DataFrame")


def _dataframe_to_records(frame) -> tuple[dict[str, Any], ...]:
    normalised = frame.astype(object).where(frame.notna(), None)
    return tuple(normalised.to_dict(orient="records"))


def _import_pandas():
    try:
        import pandas
    except ImportError as error:
        raise RuntimeError(
            "pandas interoperability requires pandas to be installed",
        ) from error
    return pandas
