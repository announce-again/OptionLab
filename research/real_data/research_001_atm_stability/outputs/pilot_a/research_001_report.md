# Research 001 Pilot A — SPY ATM volatility stability, 2020–2022

## Status

This is a completed Pilot A diagnostic, not the formal rate/dividend-enriched Research 001A result. NCX bid/mid/ask IV was reconstructed under zero rates and zero dividends after a recorded nearest-expiry and |log(K/S)| ≤ 0.40 prefilter.

## Main findings

- Short maturity is less stable. Median daily |ΔATMIV| is 1.145 volatility points at 21D, 1.021 at 45D, 0.785 at 90D, and 0.709 at 150D.
- Stress matters strongly in the descriptive data. Extreme-regime 21D instability is 4.56× the low-regime median.
- 2020 is the least stable year at 21D and 45D: medians are 1.332 and 1.338 volatility points.
- Quote uncertainty predicts later movement in the pilot. The next-day HAC coefficient on ATM IV spread is 0.597 (p=0.0002342). This is predictive association, not causality.
- Only 8.6% of valid 21D daily moves fall within the average current/previous ATM IV bid-ask interval; the corresponding 150D fraction is 29.0%.

## Coverage

The panel contains 2,973 observations. Coverage is 100.0% at 21D, 99.2% at 45D, 95.3% at 90D, and 97.8% at 150D.

## Interpretation limits

- This pilot is deliberately labelled `zero_rate_zero_dividend_diagnostic`.
- The pilot prefilter makes the fixed-expiry versus nearest-tenor comparison non-identifying.
- SPY options are American-style while NCX inversion uses the current Black–Scholes research pipeline; the approximation must be retained as a limitation.
- H4–H6 require the multi-underlying Part B datasets and are not tested here.
- Formal Research 001A still requires the 2010–2023 dataset and historical rate/dividend enrichment.

## Hypothesis log

- H1: supported_in_zero_carry_not_robust — Zero-carry ranking=[150, 90, 45, 21]; flat 4% rate/1.5% dividend ranking=[45, 90, 21, 150].
- H2: supported_across_both_carry_specs — Next-day spread coefficients: baseline=0.597443 (p=0.000234207), alternative=0.574631 (p=0.000659907).
- H3: supported_descriptively_across_carry_specs — 21D extreme/low median-instability ratios: baseline=4.56x, alternative=4.59x.
- H7: supported_ranking_differs — Stability ranking from most to least stable: IV=[150, 90, 45, 21]; total variance=[150, 90, 21, 45].
- H8: not_identified_by_pilot_design — The pilot preselected nearest expiries before inversion; its fixed-expiry subset is not a like-for-like full expiry panel.

## Carry sensitivity

The maturity ranking changes materially: baseline=[150, 90, 45, 21], alternative=[45, 90, 21, 150]. Median absolute ATM-IV level differences range from 0.438 to 1.231 volatility points across tenors. The largest change in a tenor's median daily instability is 0.706 volatility points.
