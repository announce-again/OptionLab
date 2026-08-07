# Research 001A — SPY vendor-IV replication, 2010–2023

## Status

This is the preregistered `vendor_iv_replication`, not the formal NCX rate/dividend-enriched result. Vendor OTM IV is interpolated in variance at spot ATM.

## Findings

- Median daily |ΔATMIV|: 21D=0.766, 45D=0.641, 90D=0.522, 150D=0.452 volatility points.
- Stability ranking from most to least stable is [150, 90, 45, 21].
- Extreme-regime 21D median instability is 4.17× the low-regime median.

## Limits

- Vendor IV model details are not fully documented and vendor IV is not treated as truth.
- Bid/ask IV uncertainty cannot be reconstructed from vendor IV alone.
- Formal conclusions remain conditional on NCX reconstruction with historical carry enrichment.
