# Stage 3.2 Volatility Term Structure

`VolatilityTermStructure` is a deterministic representation of expiry-level
Stage 3.2 results. It is not a continuous surface.

## Boundary

```text
VolatilitySmile
-> local ATM/skew/curvature result
-> delta/RR/BF result
-> VolatilityTermStructurePoint
-> symbol and valuation-snapshot grouping
```

Each point retains the complete source smile, `SmileMetricResult`, and
`SmileDeltaMetrics`. Convenience properties expose ATM IV, ATM total variance,
total-variance skew, curvature, RR25, and BF25 without discarding component
statuses or failure reasons.

`build_volatility_term_structures` groups by underlying symbol and valuation
timestamp, then orders points by maturity and expiration. Every input smile is
preserved even when one or more metrics fail.

## Duplicate Policy

The explicit v1 policy is `DuplicateTermStructurePolicy.ERROR`. Duplicate expiry
or maturity analyses in one symbol/snapshot group are rejected rather than
resolved from input order.

## Non-Goals

This representation performs no maturity interpolation, smoothing, missing-value
filling, calendar monotonicity enforcement, arbitrage repair, strike interpolation,
or surface construction. Those operations belong to Stage 3.3 or Stage 3.4.

## Export

Records and DataFrames contain one row per expiry with local metric values and
independent statuses plus RR25/BF25 values and statuses. Missing values remain
missing rather than being encoded as zero.

