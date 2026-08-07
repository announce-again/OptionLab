# Research 001 Pilot A — SPY ATM volatility stability, 2020–2022

## Status

This is a completed Pilot A diagnostic, not the formal rate/dividend-enriched Research 001A result. NCX bid/mid/ask IV was reconstructed under zero rates and zero dividends after a recorded nearest-expiry and |log(K/S)| ≤ 0.40 prefilter.

## Main findings

- Short maturity is less stable. Median daily |ΔATMIV| is 1.277 volatility points at 21D, 1.216 at 45D, 1.267 at 90D, and 1.415 at 150D.
- Stress matters strongly in the descriptive data. Extreme-regime 21D instability is 4.59× the low-regime median.
- 2020 is the least stable year at 21D and 45D: medians are 1.527 and 1.482 volatility points.
- Quote uncertainty predicts later movement in the pilot. The next-day HAC coefficient on ATM IV spread is 0.575 (p=0.0006599). This is predictive association, not causality.
- Only 8.2% of valid 21D daily moves fall within the average current/previous ATM IV bid-ask interval; the corresponding 150D fraction is 19.4%.

## Coverage

The panel contains 2,973 observations. Coverage is 100.0% at 21D, 99.2% at 45D, 95.3% at 90D, and 97.8% at 150D.

## Interpretation limits

- This pilot is deliberately labelled `zero_rate_zero_dividend_diagnostic`.
- The pilot prefilter makes the fixed-expiry versus nearest-tenor comparison non-identifying.
- SPY options are American-style while NCX inversion uses the current Black–Scholes research pipeline; the approximation must be retained as a limitation.
- H4–H6 require the multi-underlying Part B datasets and are not tested here.
- Formal Research 001A still requires the 2010–2023 dataset and historical rate/dividend enrichment.

## Hypothesis log

- H1: supported_in_pilot — Median |ΔATMIV| declines from 0.012768 at 21D to 0.014150 at 150D.
- H2: supported_in_pilot — Next-day ATM-spread HAC coefficient=0.574631, p=0.000659907.
- H3: supported_descriptively — 21D extreme-regime median instability is 4.59x the low-regime value.
- H7: supported_ranking_differs — Stability ranking from most to least stable: IV=[45, 90, 21, 150]; total variance=[90, 150, 21, 45].
- H8: not_identified_by_pilot_design — The pilot preselected nearest expiries before inversion; its fixed-expiry subset is not a like-for-like full expiry panel.
