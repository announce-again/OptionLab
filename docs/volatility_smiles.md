# Stage 3.2 Smile Representation and Selection

Stage 3.2 consumes `ImpliedVolatilityChain` objects produced by Stage 3.1. It does
not read provider CSV directly and does not solve implied volatility again.

## Boundary

```text
cleaned option prices
-> ImpliedVolatilityChain
-> build_volatility_smiles
-> SmileSelectionResult
   -> expiry-level VolatilitySmile objects
   -> per-observation SmileSelectionDiagnostic objects
   -> inconsistent-group SmileGroupDiagnostic objects
```

Stage 3.1 retains all interpretable bid, midpoint, and ask IV observations. Stage
3.2 decides which observations enter a research smile and records why every other
observation was excluded.

## First-Round API

The representation and selection release provides:

- `VolatilitySmilePoint`
- `VolatilitySmile`
- `SmileSelectionConfig`
- `SmileSelectionDiagnostic`
- `SmileGroupDiagnostic`
- `SmileSelectionResult` and summary counts
- `build_volatility_smiles`
- deterministic records and pandas DataFrame conversion for selected points
- deterministic records and pandas DataFrame conversion for diagnostics
- deterministic records and pandas DataFrame conversion for group diagnostics

`SmileSelectionResult` retains the complete `SmileSelectionConfig` used to build
it so downstream research can audit the selection policy and numerical tolerances.

Smiles are grouped by underlying, enrichment valuation timestamp, and expiration.
The per-row quote timestamp is retained for duplicate resolution and export; it is
not used as the snapshot grouping key.

## Default Selection Policy

The default policy uses midpoint IV and requires a two-sided quote. It excludes
failed IV results and Stage 3.1 observations carrying `LOW_VEGA`,
`VEGA_UNAVAILABLE`, or `UPPER_BOUND_IV`.

OTM selection uses the forward boundary:

- puts are selected when `log(K/F) < 0`;
- calls are selected when `log(K/F) > 0`;
- both sides are eligible inside the configured ATM tolerance.

Duplicate observations for the same option type and strike retain the latest quote
timestamp. Remaining call/put overlap at one strike uses the explicit
`DuplicateStrikePolicy`. The default `PREFER_OTM` selects the financially OTM side
away from the forward and uses liquidity within the ATM tolerance. Alternatives are
`MOST_LIQUID`, `PREFER_CALL`, and `PREFER_PUT`. The representation always retains one
point per strike, including when `otm_only=False`.

`PREFER_OTM` resolves call/put overlap as follows:

```text
K > F: prefer call
K < F: prefer put
inside ATM tolerance: both are ATM-eligible, then use liquidity rank
```

Optional liquidity filters cover maximum relative spread, bid and ask size, session
volume, and open interest. Filtering never mutates or deletes the Stage 3.1 chain.

## ATM Semantics

The representation keeps three concepts separate:

```text
nearest-forward observed point
!= observed point inside the ATM tolerance
!= interpolated ATM volatility
```

`nearest_atm_point` is always the selected point minimising `abs(log(K/F))` when a
smile has points. `observed_atm_point` is non-null only when that point is inside
`atm_log_moneyness_tolerance`. Records export `is_nearest_atm` and
`is_observed_atm` separately. This stage does not interpolate ATM volatility.

## Market-State Consistency

Selection first removes unavailable or disallowed IV observations, applies liquidity
filters, and resolves older records for each strike and option type. Only the latest
eligible candidates then participate in the market-state check. A stale or otherwise
excluded quote therefore cannot reject an otherwise consistent smile.

The remaining candidates validate `time_to_maturity`, `spot_price`, `forward_price`,
and both discount factors with configurable absolute and relative `isclose`
tolerances. An inconsistent candidate group does not produce a smile. It produces an
`INCONSISTENT_MARKET_STATE` `SmileGroupDiagnostic` containing the affected fields and
all group-rejected IV quotes.

Summary counts preserve the accounting identity:

```text
input quotes = selected points + quote exclusions + group-rejected quotes
```

The summary reports quote and group diagnostic counts separately and includes
`group_reason_counts` for each `SmileGroupDiagnosticReason`.

## Selection Diagnostics

A quote-level exclusion receives one structured diagnostic with one or more reasons:

```text
FAILED_IV
MISSING_BID
MISSING_ASK
LOW_VEGA
VEGA_UNAVAILABLE
UPPER_BOUND_IV
NOT_OTM
LIQUIDITY_FILTER
STALE_QUOTE
DUPLICATE_STRIKE
NON_FINITE_IV
```

Each diagnostic retains the original `ImpliedVolatilityQuote`, selected IV side,
Stage 3.1 status, failure reason, and diagnostic flags.

Selected points remain usable when an optional coordinate is unavailable. Point
flags explain these cases:

```text
DELTA_BOUNDARY_UNAVAILABLE
DELTA_NUMERICAL_FAILURE
IV_SPREAD_UNAVAILABLE
```

`VolatilitySmilePoint` requires finite, non-negative IV. A legal Stage 3.1 upper-bound
`+inf` therefore remains representable in the IV chain but cannot enter a smile.

## Coordinates and Export

Selected points expose strike, Black-Scholes-Merton delta, spot moneyness, forward
moneyness, and `log(K/F)`. Exports also retain bid, midpoint, and ask IV, selected
Vega, bid-ask IV spread, liquidity fields, source status, point flags, and separate
nearest/observed ATM markers. Smile records also retain the ATM and market-state
tolerances used to validate the representation.

## Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe examples\market_data\11_stage_3_2_volatility_smiles.py --rows 50000
```

The example writes the deterministic synthetic input, selected points,
selection/group diagnostics, all Stage 3.2 metric tables, term structures, and
summary hashes under `.tmp/examples_output/volatility_smiles/`. It reports each
pipeline and analysis throughput boundary separately.

## Downstream Analysis

`smile_metrics.py`, `delta_metrics.py`, and `term_structure.py` consume this
representation for ATM/local metrics, signed-delta metrics, RR/BF, and expiry term
structures. `analyze_volatility_smiles` runs those layers without returning to raw
quotes. No Stage 3.3 surface is constructed here.
