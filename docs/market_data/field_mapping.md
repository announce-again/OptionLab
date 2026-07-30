# Stage 2.0a - Field Mapping Survey

## Objective

Track how source fields map to the future canonical market-data schema. This
table is a deliverable of Stage 2.0a, not a separate roadmap stage. It is
preliminary and should be updated as fixtures are collected.

## Status

**Field Survey Preliminary**

## Field Classification

Use these classifications during reconnaissance:

- `Canonical`: required by the core domain model.
- `Optional canonical`: useful in the domain model but may be absent.
- `Source metadata`: preserve for traceability, but do not treat as a core
  domain field.
- `Aggregate/bar data`: interval or session aggregate data that should not be
  treated as an individual quote or trade event.
- `Derived`: compute internally rather than trusting the provider as the
  authoritative value.
- `Ignored`: do not carry forward unless a later use case requires it.

## Identity Concepts

Do not collapse option identity into a single ambiguous `option_symbol` field.
Track at least these concepts separately:

- Source instrument identifier, such as provider ticker, raw symbol, or
  instrument ID.
- Canonical contract identity, built from explicit contract attributes when
  available.
- Display or standardized symbol, such as OCC/OSI-style output.

The canonical identity may start with underlying, expiration, strike, option
type, exercise style, and multiplier, but this may still be insufficient for
adjusted contracts. Source identifiers and deliverable information must remain
available for traceability.

## Exchange Concepts

Do not model a single vague `exchange` field. The survey distinguishes:

- Listing exchange: where the contract is listed.
- Quote venue: where bid or ask liquidity is observed.
- Trade venue: where a trade occurred.

Provider-level publisher or dataset identifiers should be preserved separately
from exchange semantics.

## Volume Concepts

Do not model all source volume fields as a single known `volume` concept.

| Concept | Meaning |
| --- | --- |
| Interval volume | Volume within a specified observation interval. |
| Session volume | Current trading-day cumulative volume. |
| Previous-session volume | Prior completed trading-day volume. |
| Unspecified provider volume | Volume whose aggregation period is not sufficiently documented. |

Stage 2.1 may choose a narrow first version such as `session_volume`, but Cboe
interval volume must not be loaded into it unconditionally.

## Source Comparison Table

| Canonical concept | Cboe flat quote intervals | Massive/Polygon chain snapshot | Databento separated schemas | Initial classification | Notes |
| --- | --- | --- | --- | --- | --- |
| Underlying symbol | `Underlying Symbol` | Path parameter plus `underlying_asset.ticker` | `underlying` or `asset` in definitions | Canonical | Need stable symbol normalization policy. |
| Source instrument identifier | `Root` plus source row fields | `details.ticker` | `raw_symbol`, `instrument_id` | Source metadata | Preserve provider identity separately from canonical contract identity. |
| Canonical contract identity | Construct from explicit row fields | Construct from `details` fields | Construct from definitions and reference interpretation | Canonical | Do not rely only on symbol parsing when explicit fields exist. |
| Display or standardized symbol | May be reconstructed | `details.ticker` may be provider-style OCC-like ticker | `raw_symbol` uses OCC/OSI-style symbology for OPRA | Optional canonical | Useful for display and cross-checks. |
| Expiration | `Expiration` | `details.expiration_date` | `expiration` | Canonical | Normalize canonical expiration to date unless time semantics are required separately. |
| Strike | `Strike` | `details.strike_price` | `strike_price` | Canonical | Databento may use scaled integer price conventions. |
| Option type | `Option Type` | `details.contract_type` | `instrument_class` and/or CFI/reference interpretation; `raw_symbol` as fallback cross-check | Canonical | Normalize to `CALL` or `PUT`; do not assume only one Databento field is authoritative before fixture validation. |
| Exercise style | Not listed in product field list | `details.exercise_style` | May require reference data interpretation | Optional canonical | Defaulting would be risky; preserve unknown explicitly. |
| Contract multiplier | Not listed in product field list | `details.shares_per_contract` | May require definition fields | Optional canonical | Semantically important, but do not default to 100 without source evidence. |
| Listing exchange | Not directly listed in product field list | May require contract reference endpoint | Definition/reference metadata, if available | Optional canonical | Keep separate from quote and trade venues. |
| Quote venue | OPRA/NBBO interval data rather than venue-specific quote field | Quote object may expose bid/ask venue fields in some APIs or plans | BBO/MBP publisher and venue metadata | Optional canonical | Consolidated NBBO is not the same as a listing exchange. |
| Trade venue | Not a concrete trade-event field in interval file | `last_trade.exchange` | Trades schema publisher and venue metadata | Optional canonical | Trade venue is not contract listing exchange. |
| Currency | Not listed in product field list | Not in chain snapshot sample | `strike_price_currency` | Optional canonical | May be needed before multi-currency support. |
| Bid | `Bid` | `last_quote.bid` | BBO/MBP quote schemas | Canonical | Missing and zero conventions must be source-specific. |
| Bid size | `Bid Size` | `last_quote.bid_size` | BBO/MBP quote schemas | Optional canonical | Useful for liquidity filters. |
| Ask | `Ask` | `last_quote.ask` | BBO/MBP quote schemas | Canonical | Missing and zero conventions must be source-specific. |
| Ask size | `Ask Size` | `last_quote.ask_size` | BBO/MBP quote schemas | Optional canonical | Useful for liquidity filters. |
| Last traded price | No direct event field | `last_trade.price` | Trades schema | Optional canonical if `OptionTrade` is in Stage 2.1 | Cboe `Close` is interval aggregate data, not a last-trade event. |
| Trade size | No direct event field | `last_trade.size` | Trades schema | Optional canonical if `OptionTrade` is in Stage 2.1 | If first canonical slice excludes `OptionTrade`, exclude all last-trade fields coherently. |
| Trade timestamp | No direct event field | `last_trade.sip_timestamp` | Trades schema timestamps | Optional canonical if `OptionTrade` is in Stage 2.1 | Keep separate from quote timestamp. |
| Interval open | `Open` | Not a chain-snapshot trade event | OHLCV schema if selected | Aggregate/bar data | Candidate for future `OptionIntervalBar`, not first quote model. |
| Interval high | `High` | Not a chain-snapshot trade event | OHLCV schema if selected | Aggregate/bar data | Candidate for future `OptionIntervalBar`. |
| Interval low | `Low` | Not a chain-snapshot trade event | OHLCV schema if selected | Aggregate/bar data | Candidate for future `OptionIntervalBar`. |
| Interval close | `Close` | Not applicable | OHLCV schema if selected | Aggregate/bar data | Do not load into `OptionTrade.price`. |
| Interval volume | `Trade Volume` | Not applicable | OHLCV schema if selected | Aggregate/bar data | Requires aggregation-period metadata. |
| Session volume | Not directly represented by interval rows | `day.volume` | Statistics or derived from trades | Optional canonical | Requires explicit aggregation period. |
| Previous-session volume | Not directly represented by interval rows | Possibly prior-day bar endpoints, not chain snapshot core | Statistics schema if available | Optional canonical | Keep separate from current session volume. |
| Open interest | Optional `Open Interest` | `open_interest` | Statistics schema | Optional canonical | Must carry `open_interest_date` or unknown reference date; not quote timestamp. |
| Implied volatility | Optional `Implied Volatility` | `implied_volatility` | Derived externally or computed internally | Source metadata | Do not infer percent/decimal conversion from magnitude alone. |
| Provider Greeks | Optional calculated Greeks | `greeks` object | Provider/calculation dependent | Source metadata | Do not use as authoritative model outputs. |
| Quote timestamp | `Quote Datetime` | `last_quote.last_updated` | Quote schema timestamps | Canonical | Normalize to timezone-aware UTC. |
| Snapshot timestamp | Grouping key from `Quote Datetime` | Response/request time or nested timestamps | Dataset request window | Optional canonical | Need ingestion timestamp separately. |
| Underlying spot | `Active Underlying Price` when calcs selected, or derived from underlying bid/ask | `underlying_asset.price` | Joined underlying data | Optional canonical at ingestion; required for selected enrichment | Option quotes can exist without synchronized underlying spot. |
| Underlying bid/ask | `Underlying Bid`, `Underlying Ask` | Not the main sample field pair | Joined underlying data | Optional canonical | Useful when spot is unavailable or synthetic midpoint is needed. |
| Midpoint | Not listed as a source field | `last_quote.midpoint` | Derived from bid/ask | Derived | Compute internally for consistency. |
| Break-even price | Not listed | `break_even_price` | Not core schema | Source metadata | Provider-specific convenience field. |
| Fair market value | Not listed | `fmv` | Not core schema | Source metadata | Provider proprietary field; not canonical. |

## Normalization Requirements Discovered

- Cboe interval files must be grouped by `Quote Datetime`; one file may produce
  multiple `OptionChainSnapshot` objects.
- Cboe OHLC and interval volume fields are aggregate/bar data and must not be
  mapped to single-trade fields.
- Volume requires an aggregation period. Unknown source volume semantics should
  remain explicit rather than being silently coerced.
- Open interest requires its own observation date or reference time. It must
  not inherit the quote timestamp by default.
- Exchange semantics must be split into listing exchange, quote venue, and
  trade venue.
- Databento option type should be inferred from explicit reference semantics
  and cross-checked against raw OCC/OSI-style symbols where available.
- Databento-style null price fixtures should cover raw integer sentinels,
  converted `NaN`, and zero size for missing depth.
- Massive/Polygon implied volatility should remain provider metadata until a
  source-level unit convention is verified; do not divide by 100 merely because
  a value exceeds `1`.

## Immediate Follow-Up Tasks

- Construct the Stage 2.0b fixture set.
- Record fixture provenance and redistribution constraints.
- Add abnormal quote cases as labelled synthetic mutations when real samples do
  not naturally contain them.
- Convert this preliminary mapping into canonical schema requirements before
  Stage 2.1 begins.
