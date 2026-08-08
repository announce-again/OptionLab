# Research 001A — full-history NCX reconstruction

Carry specification: `treasury_trailing_dividend_yield`.

Raw bid/ask quotes were inverted with the NCX Stage 3.1 pipeline and passed to Stage 3.2 ATM analysis for every eligible 7–180D expiry.

## Findings

- Median daily |ΔATMIV| (vol points): 21D=0.883, 45D=0.768, 90D=0.512, 150D=0.413.
- Stability ranking, most to least stable: [150, 90, 45, 21].
- Extreme-regime 21D instability is 4.06× the low-regime median.

Treasury constant-maturity yields remain financing proxies, and the projected SPY distribution schedule uses the last amount known at each quote date.
