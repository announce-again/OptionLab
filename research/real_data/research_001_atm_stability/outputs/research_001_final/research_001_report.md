# Research 001 — How Stable Is At-the-Money Implied Volatility?

## Execution status

The data freeze, provenance manifests, audits, deterministic panels, SPY NCX pilot, SPY 2010–2023 vendor-IV replication, and five-underlying vendor-IV extension are complete. The formal 2010–2023 NCX result remains pending historical rate/dividend enrichment; vendor IV is therefore reported as replication evidence, not truth.

## Main findings

1. In the 2010–2023 SPY vendor replication, median daily |ΔATMIV| declines from 0.766 vol points at 21D to 0.452 at 150D.
2. In 2020, the corresponding medians are 1.346 and 0.646 vol points.
3. NCX bid/ask uncertainty explains only a minority of observed moves: depending on tenor, 8.6%–29.0% fall inside the average two-day IV spread. The next-day spread coefficient is 0.597 (p=0.0002342).
4. H1 is carry-sensitive. Zero-carry NCX ranks 150D most stable, while the flat 4% rate / 1.5% dividend-yield diagnostic ranks 45D most stable and 150D least stable.
5. At 21D, ETFs have lower absolute instability (1.109 versus 2.046 vol points), but higher relative instability (5.41% versus 4.53%).
6. The two SPY Kaggle sources agree closely on levels in their overlap: correlations range from 1.000 to 1.000; median absolute level differences range from 0.000 to 0.000 vol points.

## Cross-underlying result

Median absolute daily changes (21D, vol points): SPY=1.076, QQQ=1.179, AAPL=1.567, NVDA=1.936, TSLA=2.914.

QQQ is retained with an explicit coverage warning: the downloaded file begins on 2021-01-04, so QQQ comparisons use 2021–2022 support rather than the advertised 2020–2022 window.

## Hypothesis log

- H1: **conditional_not_robust** — Shorter tenors are less stable in long vendor IV and zero-carry NCX, but the flat 4%/1.5% carry sensitivity changes the maturity ranking.
- H2: **supported_in_spy_pilot** — ATM bid-ask IV spread predicts next-day absolute change in both NCX carry specifications (positive coefficients, p<0.001).
- H3: **supported_descriptively** — Extreme-regime 21D median instability is about four times the low-regime value in both long vendor IV and NCX pilot evidence.
- H4: **absolute_supported_relative_not_supported** — ETFs have smaller absolute changes, but at 21D their median relative instability exceeds the stock aggregate.
- H5: **supported_descriptively** — High-IV stocks show much larger absolute changes; relative differences shrink or reverse.
- H6: **exploratory_not_confirmatory** — TSLA retains a positive fixed effect, but five clusters are insufficient for confirmatory inference.
- H7: **supported** — ATM IV and relative total-variance stability produce different tenor rankings.
- H8: **not_identified** — Nearest-tenor and fixed-expiry summaries differ, but design suitability is not a causal or statistical hypothesis in the current panels.

## Interpretation

The strongest evidence is that stress regimes and short maturities amplify ATM-IV movement, and that quote uncertainty predicts—but does not fully contain—next-day changes. The weakest evidence is the exact maturity ranking under reconstructed IV: it changes materially with the carry specification, so no unconditional H1 conclusion is justified yet.

## Required next step for a formal paper

Enrich every date/expiry with reproducible historical discount and dividend curves, run the full 2010–2023 NCX inversion, then add true constant-maturity 30D/60D/90D total-variance interpolation. Until that is done, the long-history and cross-underlying results remain explicitly labeled `vendor_iv_replication`.
