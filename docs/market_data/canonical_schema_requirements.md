# Stage 2.0d - Canonical Schema Requirements

## Objective

Record what Stage 2.1 canonical market-data models must support based on the
Stage 2.0 source survey and fixture construction.

This document defines requirements only. It does not introduce dataclasses,
parsers, validators, pandas interfaces, or cleaning policies.

## Status

**Complete**

## Contract Requirements

- Contract identity must not rely solely on parsing provider symbols.
- Explicit underlying, expiration, strike, and option type fields must be
  supported.
- Provider instrument identifiers must be preservable separately from canonical
  contract identity.
- Display or standardized symbols should be preservable separately from source
  identifiers.
- Contract multiplier may be unknown and must not default to `100` without
  source evidence.
- Exercise style may be unknown.
- Currency may be unknown.
- Listing exchange must not be confused with quote venue, trade venue,
  publisher, or dataset.
- Canonical identity should allow later extension for adjusted contracts and
  non-standard deliverables.
- Databento-style separated definitions and dynamic quote records must be
  representable through a stable join key such as `instrument_id`.

## Quote Requirements

- Bid and ask may be independently absent.
- Zero bid or ask prices must remain structurally representable.
- Negative quote values should be preserved in raw ingestion records, but
  rejected at the canonical model boundary.
- Crossed and locked markets must be representable before cleaning.
- Quote timestamps must support timezone-aware UTC datetimes.
- Bid and ask sizes are optional.
- Bid and ask venues may differ.
- Missing book levels may appear as source-specific sentinels, converted `NaN`,
  or absent fields.
- Quote records must preserve enough source metadata to explain normalization
  choices.

## Trade Requirements

- Stage 2.1 must explicitly decide whether `OptionTrade` belongs in the first
  canonical slice.
- If `OptionTrade` is included, trade price, size, timestamp, and trade venue
  should be modelled together.
- Trade prices must be non-negative finite values.
- Cboe interval `Close` must not be loaded into `OptionTrade.price`.
- Trade timestamps must remain separate from quote timestamps.

## Snapshot Requirements

- One source file may contain multiple logical snapshots.
- Cboe-style interval files must be groupable by observation timestamp.
- A paginated API response may represent only part of one chain.
- Underlying data may be supplied once per snapshot, repeated per contract, or
  absent.
- Canonical snapshots should allow `underlying_quote` to be absent.
- Contract definitions and dynamic quotes may need to be joined before a
  complete canonical snapshot can be produced.
- Deterministic ordering must not depend on provider row order alone.

## Underlying Requirements

- Underlying spot is optional at contract/quote ingestion time.
- Underlying price, bid, and ask must be non-negative finite values when
  present.
- Underlying spot or forward is required only for selected enrichment
  operations such as moneyness, intrinsic value, and arbitrage bounds.
- Underlying bid and ask may be available without a provider midpoint.
- Underlying timestamps may differ from option quote timestamps.

## Statistical Field Requirements

- Volume must carry aggregation semantics.
- The first canonical model must not collapse interval volume, session volume,
  previous-session volume, and unspecified provider volume into one field.
- Open interest must not be assumed to share the quote timestamp.
- Open interest should carry `open_interest_date`, `as_of_date`, or an
  explicitly unknown reference date.
- Provider implied volatility and Greeks are non-authoritative metadata at this
  stage.
- Provider IV unit conversion must rely on documented source convention, not
  value magnitude.
- Provider convenience fields such as break-even price and fair market value
  should remain source metadata unless a later stage promotes them.

## Aggregate And Bar Data Requirements

- Cboe `Open`, `High`, `Low`, `Close`, and `Trade Volume` are interval
  aggregate data.
- Aggregate/bar data should not be mixed into the first canonical quote model
  unless the model explicitly includes an interval bar type.
- A future `OptionIntervalBar` can be considered after the quote model is
  stable.

## Exchange And Venue Requirements

- Use distinct concepts for listing exchange, quote venue, trade venue,
  publisher, and dataset.
- A single `exchange: str | None` field would be ambiguous and should be
  avoided in Stage 2.1.
- OPRA or consolidated NBBO data should not be treated as a contract listing
  exchange.
- Provider numeric exchange codes should be preserved as source metadata until
  a mapping layer exists.

## Metadata Requirements

- Every canonical object produced from external data should retain data-source
  metadata sufficient for traceability.
- Raw source rows or source record identifiers should be preservable at the
  boundary layer.
- Synthetic fixture records must remain distinguishable from observed source
  records.
- Ingestion timestamp and valuation timestamp are distinct concepts.

## Requirements For Stage 2.1 Design

Stage 2.1 should define at minimum:

- `OptionType`
- `ExerciseStyle`
- `OptionContract`
- `OptionQuote`
- `UnderlyingQuote`
- `OptionChainSnapshot`
- Source metadata structures
- Contract identity and sorting keys
- Call-put pairing keys

Stage 2.1 should postpone:

- CSV parsing.
- pandas conversion.
- Quote cleaning policies.
- Derived fields such as midpoint, moneyness, and intrinsic value.
- Provider-specific normalization rules beyond type definitions needed by the
  canonical model.
- Interval-bar modelling unless it is required to keep quote semantics clean.
