# Research 001A — full-history NCX reconstruction

Carry specification: `treasury_projected_dividend_schedule`.

Raw bid/ask quotes were inverted with the NCX Stage 3.1 pipeline and passed to Stage 3.2 ATM analysis for every eligible 7–180D expiry.

## Findings

- Median daily |ΔATMIV| (vol points): 21D=NA, 45D=0.432, 90D=0.322, 150D=0.283.
- Stability ranking, most to least stable: [150, 90, 45].
- Extreme-regime 21D instability is nan× the low-regime median.

Treasury constant-maturity yields remain financing proxies, and the projected SPY distribution schedule uses the last amount known at each quote date.
