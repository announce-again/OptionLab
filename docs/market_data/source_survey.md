# Stage 2.0a - Source Selection and Field Survey

## Objective

Select representative option-market data formats and document their field
structure before implementing canonical models or ingestion code.

This is a reconnaissance document. It records source-format observations,
schema questions, and fixture candidates. It is not a provider integration
plan and does not require live APIs, credentials, SDKs, or network access at
runtime.

## Status

**Substantially Complete**

Completed:

- Three structurally distinct formats selected.
- Preliminary field mapping completed.
- Important semantic ambiguities documented.

Remaining before closure:

- Correct interval-versus-snapshot assumptions in fixture design.
- Separate volume and exchange concepts in schema requirements.
- Record Databento null-price conventions in normalization fixtures.
- Finalize fixture targets through Stage 2.0b.

## Selection Criteria

The survey should cover structural diversity rather than provider count alone.
The initial source set should include:

- A flat interval table with one row per contract per observation time.
- A nested option-chain snapshot with contract, quote, trade, and underlying
  fields grouped under each result.
- A separated market-data format where contract definitions, quotes, trades,
  statistics, and open interest can arrive as distinct schemas.

## Initial Source Candidates

| Source | Format style | Why it matters | Current decision |
| --- | --- | --- | --- |
| Cboe DataShop Option Quotes | Flat interval table | Clear one-row-per-contract-per-observation-time quote file with NBBO fields, interval OHLC, interval volume, optional IV/Greeks, optional open interest, and underlying fields. | Use as flat interval CSV-style reference format. |
| Massive/Polygon Option Chain Snapshot | Nested REST JSON | Chain endpoint nests contract details, quote, trade, greeks, implied volatility, open interest, and underlying asset data. | Use as nested snapshot reference format. |
| Databento OPRA schemas | Separated schemas | Definitions, quotes/BBO, trades, and statistics are represented as separate schemas keyed by instrument identifiers. | Use as separated-schema reference format. |

## Source Notes

### Cboe DataShop Option Quotes

Reference: https://datashop.cboe.com/option-quote-intervals

Observed shape:

- Flat interval dataset.
- One row represents one option contract at one observation time, not one
  unique contract across the whole file.
- Fields include underlying symbol, quote datetime, root, expiration, strike,
  option type, OHLC prices, trade volume, bid size, bid, ask size, ask,
  underlying bid, and underlying ask.
- `Open`, `High`, `Low`, `Close`, and `Trade Volume` are interval aggregate
  fields, not a concrete last-trade event.
- Optional calculated fields include active underlying price, implied
  volatility, and Greeks.
- Optional open-interest field is available when selected.
- Dataset documentation notes underlying-data exceptions for index products.

Reconnaissance value:

- Good primary candidate for canonical quote fields.
- Good source for flat CSV fixtures.
- Forces ingestion to group by `Quote Datetime`:

```text
Cboe interval file
    -> group by Quote Datetime
one OptionChainSnapshot per timestamp
```

- Useful for deciding whether underlying spot should be row-level or
  snapshot-level canonical data.

Open questions:

- Exact file delimiter and sample-file redistribution terms.
- Timestamp timezone and interval-end convention.
- Whether bid/ask zero is an observed quote or missing-value convention.
- Whether optional open interest has an explicit observation date, prior
  session date, or only file-level context.

### Massive/Polygon Option Chain Snapshot

Reference: https://massive.com/docs/rest/options/snapshots/option-chain-snapshot

Observed shape:

- Nested JSON response under a `results` array.
- Contract attributes are grouped under `details`.
- Quote data is grouped under `last_quote`.
- Trade data is grouped under `last_trade`.
- Underlying data is grouped under `underlying_asset`.
- Implied volatility and open interest are top-level fields inside each
  contract snapshot result.
- Chain responses may include `next_url`; one response page should not be
  assumed to contain the full chain.
- Documentation describes U.S. options timestamps as Unix timestamps in UTC.
- Greeks can be absent in some circumstances, so they should not be treated as
  required canonical market-data inputs.
- Provider documentation describes implied volatility semantically, but does
  not establish a universal bounded range from the examples alone. Values must
  not be converted from percent merely because they exceed `1`.
- Open interest is not quote-time data; it should carry its own reference date
  when known, or an explicitly unknown reference date otherwise.

Reconnaissance value:

- Good primary candidate for nested JSON fixtures.
- Forces separation between contract identity, quote data, trade data,
  provider-calculated fields, and underlying data.
- Useful for deciding how much provider-derived data to preserve as metadata.

Open questions:

- Whether implied volatility is represented as a decimal volatility or percent
  value in all responses.
- How missing `last_quote`, `last_trade`, or `greeks` fields appear in raw
  responses.
- Whether pagination can split one logical chain snapshot. Fixture samples
  should preserve `next_url` structure.

### Databento OPRA Schemas

Reference: https://databento.com/docs/knowledge-base

Observed shape:

- Data is organized by schemas rather than a single option-chain table.
- Instrument definitions include fields such as raw symbol, expiration,
  underlying, strike price, instrument class, security type, and currency
  fields.
- Quote and trade information can be represented through market-data schemas
  such as BBO, MBP, TBBO, and trades.
- Statistics can include daily volume, open interest, settlement, and official
  prices.
- Prices and timestamps may use scaled integer and nanosecond conventions.
- Raw DBN null prices may use integer sentinel values, while client-library
  floating conversion may expose them as `NaN`.
- A zero size can accompany a missing book level and must not by itself be
  interpreted as a valid zero-price quote.
- OPRA raw symbols use OCC/OSI-style symbology and can cross-check, but should
  not replace, explicit reference fields.

Reconnaissance value:

- Good primary candidate for separated-schema fixtures.
- Forces a canonical design that does not assume every row contains both
  contract reference data and quote data.
- Useful for deciding whether canonical contract identity should rely on
  provider symbols, instrument IDs, or parsed OCC-style symbols.

Open questions:

- Which exact schemas should be represented in the first fixture set.
- How to model joins between definitions, quotes, trades, and statistics.
- Whether fixture samples can be reduced or reconstructed without licensing
  issues.

## Provisional Source Selection

The first field survey should use these three formats:

1. Cboe DataShop Option Quotes for a flat table.
2. Massive/Polygon Option Chain Snapshot for nested JSON.
3. Databento OPRA-style definitions plus market-data/statistics schemas for
   separated reference and quote data.

This selection covers the minimum structural diversity needed for Stage 2.0a:

- Flat rows.
- Nested records.
- Separated contract definitions and dynamic market data.
- Optional provider-calculated fields.
- Multiple timestamp and unit conventions.

No fourth provider is needed before fixture construction.

## Fixture Candidate Plan

The first fixture set should be small and provider-neutral where licensing
requires it. Prefer reconstructed samples that preserve source structure
without redistributing large raw downloads.

Target fixture categories:

- Normal complete chain with calls, puts, multiple strikes, and multiple
  expirations.
- Cboe interval data with at least two quote datetimes, proving that a file can
  contain multiple logical snapshots.
- Missing bid or ask.
- Zero bid or ask.
- Crossed quote where `bid > ask`.
- Locked quote where `bid == ask`.
- Zero volume and missing open interest.
- Massive snapshot data with pagination metadata or a preserved `next_url`.
- Nested record with missing optional `last_trade` or `greeks`.
- Separated definitions and quotes that must be joined by a stable key.
- Databento-style null price represented both as a raw integer sentinel and as
  a converted `NaN` value.

Synthetic mutations must be labelled as synthetic and should not be presented
as observed market events.

## Open Schema Questions for Stage 2.1

- Should canonical expiration be a `date`, with last-trade and settlement time
  captured separately when available?
- Should quote timestamps and trade timestamps always be timezone-aware UTC
  datetimes?
- Should provider implied volatility be canonical, optional canonical, or
  source metadata?
- Should provider IV unit conversion ever be performed without an explicit
  source-level unit convention? Current answer should be no.
- Should bid or ask equal to zero be accepted structurally and rejected only by
  cleaning policy, or interpreted as missing during normalisation for specific
  providers?
- Should underlying spot be optional canonical data at ingestion time but
  required only for enrichment operations?
- Should contract identity distinguish source instrument identifiers,
  canonical contract identity, and display or standardized symbols?
- Should bid/ask size be included in the first canonical quote model or left as
  optional metadata?
- Should open interest be modelled as quote-time data, daily statistics, or a
  separate optional field with its own observation date or reference time?
- Should exchange semantics be split into listing exchange, quote venue, and
  trade venue from the first canonical model?
