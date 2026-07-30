# Stage 2.0c - Fixture Provenance

## Objective

Document the source inspiration, reconstruction choices, synthetic mutations,
and redistribution assumptions for the Stage 2.0b market-data fixtures.

These fixtures are schema-design artifacts. They are not real market data and
must not be interpreted as historical market events.

## Status

**Complete**

## Global Fixture Policy

- All current fixture values are synthetic.
- No fixture contains downloaded proprietary provider records.
- Source documentation was used for structural inspiration only.
- Synthetic quality cases are intentionally fabricated to exercise validation,
  normalization, and cleaning design.
- Fixtures may be redistributed with the repository because they contain no
  vendor data, credentials, API keys, account identifiers, or personal data.

## Source References

- Cboe DataShop Option Quotes: https://datashop.cboe.com/option-quote-intervals
- Massive Option Chain Snapshot: https://massive.com/docs/rest/options/snapshots/option-chain-snapshot
- Databento schemas and data formats: https://databento.com/docs/knowledge-base
- Databento OPRA equity options introduction: https://databento.com/docs/examples/options/equity-options-introduction/opra

## cboe_intervals/normal.csv

- Structural reference: Cboe Option Quote Intervals.
- Fixture type: Reconstructed flat interval table.
- Market values: Synthetic.
- Purpose:
  - Demonstrate one row per option contract per observation time.
  - Demonstrate two distinct `Quote Datetime` values.
  - Demonstrate calls and puts.
  - Demonstrate multiple expirations.
  - Demonstrate multiple strikes.
  - Demonstrate optional implied volatility and open interest columns.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - `Open`, `High`, `Low`, `Close`, and `Trade Volume` are interval aggregate
    data in this fixture, not individual trade events.
  - A parser must group by `Quote Datetime` to produce logical snapshots.

## cboe_intervals/synthetic_quality_cases.csv

- Structural reference: Reconstructed Cboe-style interval format.
- Fixture type: Synthetic mutation.
- Market values: Synthetic.
- Purpose:
  - Missing bid.
  - Missing ask.
  - Crossed quote where `bid > ask`.
  - Locked quote where `bid == ask`.
  - Zero bid and ask.
  - Zero volume.
  - Missing open interest.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - These rows are not claimed to be observed market events.
  - The fixture exists to force structured validation and cleaning diagnostics.

## massive_snapshot/normal.json

- Structural reference: Massive/Polygon Option Chain Snapshot.
- Fixture type: Reconstructed nested snapshot.
- Market values: Synthetic.
- Purpose:
  - Demonstrate nested `details`, `last_quote`, `last_trade`, and
    `underlying_asset` objects.
  - Demonstrate calls and puts.
  - Demonstrate quote and trade timestamps as large integer epoch timestamps.
  - Demonstrate `next_url` pagination metadata.
  - Demonstrate provider fields such as `break_even_price` and
    `implied_volatility`.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - `next_url` means one response page must not automatically be interpreted as
    a complete chain.
  - Provider-derived fields are source metadata until canonical requirements say
    otherwise.

## massive_snapshot/missing_optional_fields.json

- Structural reference: Massive/Polygon Option Chain Snapshot.
- Fixture type: Synthetic mutation.
- Market values: Synthetic.
- Purpose:
  - Missing `last_trade`.
  - Missing `last_quote`.
  - Missing `greeks`.
  - Missing `implied_volatility`.
  - Null `open_interest`.
  - Implied volatility value greater than `1`.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - The `implied_volatility` value of `5` is intentional. It must not be
    rescaled based only on magnitude.
  - Null open interest must not inherit the quote timestamp.

## databento_separated/definitions.csv

- Structural reference: Databento instrument definitions and OPRA raw-symbol
  conventions.
- Fixture type: Reconstructed separated reference schema.
- Market values: Synthetic.
- Purpose:
  - Demonstrate `instrument_id` as a stable join key.
  - Demonstrate `raw_symbol` as an OCC/OSI-style cross-check.
  - Demonstrate explicit underlying, expiration, strike, option type, security
    type, and currency fields.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - `instrument_class` should be interpreted with reference semantics and
    cross-checked against `raw_symbol`; it should not be the only possible
    source of call/put information.

## databento_separated/bbo.csv

- Structural reference: Databento BBO-style quote schema.
- Fixture type: Reconstructed quote schema plus synthetic null-price mutation.
- Market values: Synthetic.
- Purpose:
  - Demonstrate joining quote rows to definitions by `instrument_id`.
  - Demonstrate bid and ask prices with sizes.
  - Demonstrate raw integer price fields alongside converted floating fields.
  - Demonstrate a null bid price represented as raw integer sentinel plus
    converted `NaN`.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - Zero size with a missing price must not be interpreted as a valid zero-price
    quote.

## databento_separated/statistics.csv

- Structural reference: Databento statistics-style records.
- Fixture type: Reconstructed separated statistics schema.
- Market values: Synthetic.
- Purpose:
  - Demonstrate open interest outside the quote schema.
  - Demonstrate an `as_of_date` separate from quote timestamps.
  - Demonstrate joining statistics to definitions by `instrument_id`.
- Redistribution:
  - Contains no downloaded proprietary records.
  - Safe to include as a test fixture.
- Important:
  - Open interest must carry its own reference date or explicitly unknown
    reference time.

