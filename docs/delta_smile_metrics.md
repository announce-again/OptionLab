# Stage 3.2 Delta Smile Metrics

The delta metric layer consumes immutable `VolatilitySmile` objects. It neither
reads raw quotes nor repeats Stage 3.1 implied-volatility solving.

## Convention

Delta is signed Black-Scholes-Merton delta:

```text
call target: +d
put target:  -d
```

The default `DeltaMetricConfig` uses `d=0.25` and a delta-coordinate tolerance
of `1e-12`. Configured magnitudes must be unique finite numbers strictly between
zero and one; the config stores them in deterministic ascending order.

## Delta Interpolation

`interpolate_smile_at_delta` uses only the requested option type and excludes
points whose delta is unavailable. Usable points are ordered by strike. An exact
target match within tolerance takes precedence. Multiple exact matches are
reported as `AMBIGUOUS_DELTA_BRACKET`.

Without an exact match, only adjacent strike-ordered pairs are considered:

```text
zero brackets     -> TARGET_DELTA_NOT_BRACKETED
one bracket       -> linear IV interpolation in signed delta
multiple brackets -> AMBIGUOUS_DELTA_BRACKET
repeated delta    -> DEGENERATE_DELTA_COORDINATES
```

No delta extrapolation is performed. Linear interpolation is:

```text
weight = (target_delta - left_delta) / (right_delta - left_delta)
target_iv = left_iv + weight * (right_iv - left_iv)
```

Results preserve the smile, option type, target, source points, interpolation
weight, usable/excluded counts, method, status, and failure reason.

## RR And BF

Risk reversal uses the call-minus-put convention:

```text
RR(d) = call_iv(+d) - put_iv(-d)
```

The symmetric delta butterfly convention is:

```text
BF(d) = (call_iv(+d) + put_iv(-d)) / 2 - ATM_iv
```

Butterfly reuses the exact Stage 3.2 local ATM result passed by the aggregate
analysis. ATM interpolation is not reimplemented. RR can therefore succeed while
BF fails with `ATM_FAILED`. Call, put, RR, and BF statuses remain independent.

## Aggregate And Export

`SmileDeltaMetrics` contains call/put target results, risk reversals, and
butterflies for every configured magnitude. One failed leg or magnitude does not
fail or remove other results.

Stable records and DataFrames are available separately for delta-target IV, risk
reversals, butterflies, and combined per-smile/per-magnitude structures. Missing
metrics export as empty CSV fields or `None` records, never zero.

## Failure Reasons

Delta interpolation reports:

```text
EMPTY_SMILE
INVALID_TARGET_DELTA
NO_POINTS_FOR_OPTION_TYPE
DELTA_UNAVAILABLE
TARGET_DELTA_NOT_BRACKETED
AMBIGUOUS_DELTA_BRACKET
DEGENERATE_DELTA_COORDINATES
NON_FINITE_RESULT
```

RR/BF report invalid magnitudes, call-leg failure, put-leg failure, ATM failure,
or non-finite output independently.

