# Market Data Fixtures

These fixtures are small reconstructed samples for Stage 2.0b. They preserve
source-format structure needed for schema design, but they are not real market
data and must not be treated as observed market events.

Values are synthetic unless a future provenance file explicitly states
otherwise.

Fixture goals:

- Demonstrate Cboe-style interval files that require grouping by quote time.
- Demonstrate Massive/Polygon-style nested snapshots with optional fields and
  pagination metadata.
- Demonstrate Databento-style separated definitions, BBO, and statistics joined
  by `instrument_id`.
- Demonstrate abnormal quote cases for deterministic validation and cleaning
  design.

