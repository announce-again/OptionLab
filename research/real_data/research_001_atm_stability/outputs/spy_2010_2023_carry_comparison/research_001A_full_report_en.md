# How Stable Is SPY At-the-Money Implied Volatility Across Dates and Expiries, 2010–2023?

## Research 001A — Full Report

**Underlying:** SPDR S&P 500 ETF Trust (SPY)  
**Sample period:** January 4, 2010 to December 29, 2023  
**Frequency:** Daily end-of-day option-chain snapshots  
**Primary estimate:** NCX bid/mid/ask IV reconstruction using a Treasury curve and projected SPY cash distributions  
**Target tenors:** Nearest 21D, 45D, 90D, and 150D expiries  
**Status:** Final Research 001A report; Research 001B is outside the scope of this report

---

## Abstract

This study examines the stability of SPY at-the-money implied volatility across dates, expiries, market regimes, liquidity conditions, and carry specifications from 2010 through 2023. The primary results do not treat vendor implied volatility as ground truth. Instead, raw option bid and ask prices are enriched with historical interest-rate and dividend assumptions, inverted through NCX Stage 3.1, and passed to the NCX Stage 3.2 ATM construction. Vendor-IV replication and an alternative trailing-dividend-yield reconstruction are retained as robustness specifications.

ATM-IV stability displays a clear maturity structure. Under the baseline NCX reconstruction, median daily absolute ATM-IV changes are 0.765, 0.625, 0.503, and 0.450 volatility points at 21D, 45D, 90D, and 150D, respectively. The 21D median is 1.70 times the 150D median. The stability ranking—150D, 90D, 45D, and 21D from most to least stable—is unchanged across vendor IV, the projected-distribution NCX baseline, and the trailing-yield NCX alternative. Fixed-expiry DTE bins produce the same maturity direction. The result is therefore not an artifact of vendor analytics, a single carry convention, or nearest-expiry selection alone.

Stability also varies sharply with market conditions. The 21D median absolute change in 2020 is 1.261 volatility points, 2.32 times its 2017–2019 value. In the pre-specified extreme-IV regime, the 21D median change reaches 2.802 volatility points, 5.06 times the low-regime median. ATM bid–ask IV spreads are positively related to contemporaneous and next-observation absolute ATM-IV changes. However, only approximately 13% to 28% of daily moves fall within the average ATM-IV spread across the two dates, so static quote uncertainty alone cannot explain most observed changes.

Carry robustness is qualitative rather than quantitative. The trailing-yield specification preserves the maturity ranking but raises median instability at 45D by 0.143 volatility points, or 22.9%, relative to baseline. The maturity effect is therefore a robust market feature, while its magnitude remains sensitive to historical dividend treatment.

**Keywords:** SPY options; ATM implied volatility; volatility stability; term structure; bid–ask uncertainty; historical carry; total variance

---

## 1. Research Questions and Contribution

Research 001A addresses eight questions:

1. How much does SPY ATM IV typically change between comparable observations?
2. Is short-dated ATM IV less stable than long-dated ATM IV?
3. How much of the observed daily change falls within bid–ask IV uncertainty?
4. Does ATM-IV stability deteriorate during 2020 and high-volatility regimes?
5. Are more liquid expiries more stable?
6. Do ATM IV and ATM total variance produce the same stability ranking?
7. Do vendor IV, baseline NCX carry, and alternative NCX carry lead to the same conclusion?
8. Are the maturity results consistent between fixed-expiry and nearest-tenor designs?

The contribution is primarily empirical and infrastructural. The study freezes raw data and provenance, constructs explicit historical carry inputs, inverts bid, midpoint, and ask prices independently, records all exclusions and failures, and compares vendor and NCX specifications on matched date-tenor observations. This design separates a market maturity effect from potential vendor-model, carry, quote-quality, and tenor-selection effects.

---

## 2. Data and Provenance

### 2.1 SPY option chains

The option data are distributed through Kaggle as **SPY Options EOD Data (2010–2023)** by uploader `dudesurfin`. The frozen uploader description claims that the original source is OptionsDX and that observations are approximately 4:00 p.m. Eastern Time end-of-day snapshots. Research 001 freezes Kaggle version 2, fourteen annual Parquet files, the page README, file sizes, and SHA-256 hashes.

Kaggle is a distribution channel rather than an exchange or originating data vendor. All statements about the original source, snapshot timing, and processing depend on the frozen uploader description.

| Item | Value |
|---|---:|
| Raw wide rows | 9,468,584 |
| Unique quote dates | 3,508 |
| Unique expirations | 1,572 |
| Unique strikes | 842 |
| Date coverage | 2010-01-04 to 2023-12-29 |
| Weekend quote rows | 0 |
| Expiration-before-quote rows | 0 |
| Vendor DTE/date mismatches | 0 |

Each raw row contains both call and put fields. The adapter expands these fields into contract-level records before the NCX pipeline is applied.

### 2.2 Interest-rate data

The baseline uses the FRED DGS1MO, DGS3MO, DGS6MO, DGS1, and DGS2 Treasury constant-maturity series. For each quote date, the construction:

1. carries the most recent observation across non-release dates, subject to a maximum observed staleness of three calendar days;
2. converts percentage values to decimals;
3. linearly interpolates rates across maturity, with flat endpoint extrapolation; and
4. treats the resulting rate as a continuously compounded zero-rate proxy:

\[
D_r(t,T)=\exp[-r(t,T)T].
\]

The Treasury specification covers 100% of the eligible expiry panel. Treasury constant-maturity yields are investment-basis government yields, not SPY option financing, repo, or OIS zero rates. The resulting curve is therefore a reproducible proxy, not an exact financing curve.

Additional carry diagnostics include a flat DGS3MO curve and a flat SOFR curve. Flat DGS3MO has 100% carry coverage. SOFR begins on April 3, 2018 and covers 57.235% of full-sample expiry rows. The SOFR specification is an overnight-rate diagnostic, not a term OIS curve.

### 2.3 SPY cash distributions

SPY distribution history is taken from State Street's official historical distribution file. The sample contains 56 distributions from 2010 through 2023.

The baseline preserves realized historical ex-date timing but assigns every future payment the most recent cash distribution amount known on the quote date. It therefore avoids using future distribution amounts. The equivalent dividend discount factor is

\[
D_q(t,T)=\frac{S_t-PV_t(\text{projected cash dividends through }T)}{S_t}.
\]

The alternative specification divides cash distributions over the preceding 365 days by contemporaneous option-chain spot and uses the result as a flat trailing dividend yield. This smooths quarterly timing and tests whether the short-dated results are sensitive to a discrete distribution schedule.

The baseline still uses the eventually realized historical ex-date calendar. Future cash amounts do not leak into the baseline, but ex-date timing is not reconstructed from a point-in-time announcement archive. This is an explicit historical-backtest limitation.

### 2.4 Option-implied forward diagnostic

A near-spot put–call parity diagnostic is also calculated from paired call and put midpoints:

\[
F^{parity}_{t,T}=K+\frac{C_{mid}-P_{mid}}{D_r(t,T)}.
\]

The diagnostic covers 99.842% of carry expiries. Its median absolute difference from the baseline forward is approximately USD 0.158. SPY listed options are American-style, so early exercise, discrete distributions, and quote noise can contaminate simple put–call parity. The implied forward is therefore retained for diagnosis and is not used as a formal carry input.

---

## 3. Sample Construction and NCX Method

### 3.1 Eligibility rules

The baseline sample requires:

- 7 to 180 calendar days to expiry;
- finite positive spot and strike;
- \(|\log(K/S)|\leq 0.40\);
- at least one valid two-sided quote;
- at least five selected smile points; and
- an observed ATM point or valid left/right ATM bracket.

The DTE and moneyness scope contains 4,771,525 wide rows, equivalent to 9,543,050 potential call and put contracts. Eight quote dates from January 27 through February 5, 2010 have no usable two-sided call or put quotes. They are recorded as `NO_TWO_SIDED_QUOTES` rather than silently removed.

After these eight dates are excluded, 9,536,134 contracts enter Stage 2, 9,470,467 survive cleaning, and 8,356,199 have the required successful IV results after inversion-quality filtering.

### 3.2 IV inversion and ATM construction

For each date and expiry, bid, midpoint, and ask option prices are inverted independently through NCX Stage 3.1. NCX Stage 3.2 then constructs ATM metrics. The primary method interpolates in total-variance space,

\[
w(k,T)=\sigma^2(k,T)T,
\]

between the nearest valid smile points on opposite sides of zero log-forward moneyness.

The baseline expiry panel contains 49,142 records. Of these, 49,103 use `LINEAR_TOTAL_VARIANCE`, eight are exact `OBSERVED` ATM values, and 31 do not receive a formal ATM method. Midpoint ATM construction succeeds for 49,110 expiry records.

Both NCX expiry panels have unique date-expiry keys and positive risk-free and dividend discount factors. The trailing-yield expiry panel contains two interpolation ordering exceptions in which ATM bid IV exceeds ATM midpoint IV: a 14D expiry on June 19, 2014 and an 8D expiry on October 29, 2015. The observations are disclosed and retained rather than repaired after the fact. Neither produces an ordering exception in the final nearest-tenor panel.

### 3.3 Nearest-tenor design

| Target tenor | Maximum mismatch |
|---:|---:|
| 21D | ±7 days |
| 45D | ±10 days |
| 90D | ±15 days |
| 150D | ±25 days |

For each quote date, the successful expiry nearest the target is selected using a deterministic tie policy. Actual DTE, expiration, and tenor mismatch remain in the output. The final nearest-tenor panel contains 12,808 observations.

### 3.4 Stability measures

The primary outcome is

\[
\Delta ATMIV_{t,\tau}=ATMIV_{t,\tau}-ATMIV_{t-1,\tau},
\qquad
ATMInstability_{t,\tau}=|\Delta ATMIV_{t,\tau}|.
\]

Changes are calculated only for the same underlying and target tenor when the previous observation is comparable and both dates satisfy the tenor-mismatch policy. Additional measures are

\[
RelativeInstability=
\left|\frac{\Delta ATMIV_t}{ATMIV_{t-1}}\right|,
\]

\[
ATMIVSpread=ATMIV^{ask}-ATMIV^{bid},
\]

and

\[
\Delta w_t=ATMIV_t^2T_t-ATMIV_{t-1}^2T_{t-1}.
\]

The quote-noise diagnostic is

\[
NoiseAdjustedMove=
\frac{|\Delta ATMIV_t|}
{\tfrac12(ATMIVSpread_t+ATMIVSpread_{t-1})}.
\]

This ratio is descriptive and is not a formal significance test.

### 3.5 Market regimes

Calendar subsamples are fixed as 2010–2012, 2013–2016, 2017–2019, 2020, and 2021–2023. Volatility regimes use frozen thresholds from the pooled nearest-tenor ATM-IV distribution:

- low: ATM IV at or below 15.448%;
- medium: 15.448% to 20.814%;
- high: 20.814% to 27.341%; and
- extreme: above 27.341%.

These thresholds are the pooled 50th, 80th, and 95th percentiles. They are sample-internal descriptive regimes, not external VIX regimes or structural break estimates.

### 3.6 Regression specifications

The contemporaneous model is

\[
|\Delta ATMIV_{t,\tau}|=
\alpha+\beta_1\log(DTE)+\beta_2ATMSpread_{t,\tau}
+\beta_3|Return_t|+\beta_4PastRV_t+\beta_5HighVol_t
+\gamma_\tau+\varepsilon_{t,\tau}.
\]

The quote-uncertainty model replaces the dependent variable with the next comparable observation's absolute ATM-IV change. Both models use HAC/Newey–West standard errors with five lags. They estimate conditional association rather than causal effects.

---

## 4. Main Descriptive Results

### 4.1 ATM levels and stability by tenor

| Target tenor | Observations | Coverage | Median ATM IV | Median ATM-IV spread | Median \(|\Delta ATMIV|\) | P95 \(|\Delta ATMIV|\) | Median relative instability |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 21D | 3,234 | 92.4% | 13.873% | 0.161 vol pts | 0.765 vol pts | 3.834 vol pts | 5.442% |
| 45D | 3,318 | 94.8% | 14.655% | 0.131 vol pts | 0.625 vol pts | 2.901 vol pts | 4.213% |
| 90D | 3,332 | 95.2% | 15.839% | 0.121 vol pts | 0.503 vol pts | 2.281 vol pts | 3.104% |
| 150D | 2,924 | 83.5% | 17.025% | 0.178 vol pts | 0.450 vol pts | 1.964 vol pts | 2.612% |

Absolute changes, relative changes, and tail changes all decline with maturity. The 150D median ATM-IV spread is the widest among the target tenors, yet 150D ATM IV is the most stable. The maturity ranking therefore cannot be reduced to tighter long-dated quotes.

![Figure 1 — Stability by tenor](../spy_2010_2023_ncx_baseline/figures/figure_01_stability_by_tenor.png)

### 4.2 Fixed-expiry evidence

Tracking fixed expirations and grouping observations by actual DTE gives the same maturity direction:

| Actual DTE bin | Expiry observations | Median \(|\Delta ATMIV|\) | P95 \(|\Delta ATMIV|\) |
|---|---:|---:|---:|
| 7–30 | 22,049 | 0.858 vol pts | 4.312 vol pts |
| 31–60 | 11,637 | 0.641 vol pts | 3.114 vol pts |
| 61–120 | 8,922 | 0.503 vol pts | 2.235 vol pts |
| 121–180 | 6,502 | 0.443 vol pts | 1.942 vol pts |

The agreement between fixed-expiry and nearest-tenor results shows that the maturity effect is not produced solely by target-expiry rollover. Stage 3.3 constant-maturity interpolation is not yet complete, so the study cannot perform a final comparison among fixed expiry, nearest tenor, and true constant maturity.

![Figure 2 — Stability by actual DTE](../spy_2010_2023_ncx_baseline/figures/figure_02_stability_by_dte.png)

---

## 5. Market Conditions and the 2020 Episode

### 5.1 Calendar-period results

| Period | 21D | 45D | 90D | 150D |
|---|---:|---:|---:|---:|
| 2010–2012 | 0.912 | 0.650 | 0.526 | 0.492 |
| 2013–2016 | 0.740 | 0.596 | 0.428 | 0.408 |
| 2017–2019 | 0.543 | 0.503 | 0.446 | 0.395 |
| 2020 | 1.261 | 1.097 | 0.798 | 0.639 |
| 2021–2023 | 0.844 | 0.685 | 0.562 | 0.481 |

Entries are median daily absolute ATM-IV changes in volatility points. Relative to 2017–2019, instability in 2020 increases by 2.32 times at 21D, 2.18 times at 45D, 1.79 times at 90D, and 1.62 times at 150D. Every tenor becomes less stable, but the amplification is strongest at the front of the term structure.

### 5.2 Volatility-regime results

| Regime | 21D | 45D | 90D | 150D |
|---|---:|---:|---:|---:|
| Low | 0.554 | 0.474 | 0.366 | 0.320 |
| Medium | 1.093 | 0.856 | 0.575 | 0.494 |
| High | 1.531 | 1.030 | 0.744 | 0.604 |
| Extreme | 2.802 | 2.173 | 1.601 | 1.427 |

From the low to extreme regime, median instability rises by 5.06 times at 21D and 4.47 times at 150D. Stress affects the full term structure rather than only short-dated options.

![Figure 3 — Rolling 21-day median instability](../spy_2010_2023_ncx_baseline/figures/figure_03_rolling_stability.png)

---

## 6. Quote Uncertainty and Observed Moves

| Tenor | Median ATM-IV spread | Median noise-adjusted move | Move within average spread | Spread versus next move: Spearman |
|---:|---:|---:|---:|---:|
| 21D | 0.161 vol pts | 4.58× | 13.8% | 0.221 |
| 45D | 0.131 vol pts | 4.35× | 13.5% | 0.202 |
| 90D | 0.121 vol pts | 3.72× | 15.6% | 0.234 |
| 150D | 0.178 vol pts | 2.14× | 27.6% | 0.218 |

Quote uncertainty is a meaningful source of measurement noise, but it does not explain most daily changes. Only approximately 13% to 28% of moves are no larger than the average ATM-IV spread across the two observations. The typical absolute move is 2.1 to 4.6 times that spread.

The HAC regressions reinforce the descriptive result:

- the contemporaneous ATM-IV-spread coefficient is 0.482 with p=0.00040;
- the next-observation ATM-IV-spread coefficient is 0.701 with p=0.00023; and
- tenor-level Spearman correlations between today's spread and the next move are approximately 0.20 to 0.23.

Wider quote uncertainty is therefore associated with larger current and subsequent estimate changes. This relationship may jointly reflect illiquidity, information arrival, stress, and microstructure noise, so it should not be interpreted causally.

![Figure 4 — Quote uncertainty and next move](../spy_2010_2023_ncx_baseline/figures/figure_04_quote_uncertainty.png)

---

## 7. Liquidity Evidence

Liquidity-quintile results are not strictly monotonic. At 150D, median instability rises from 0.382 volatility points in the narrowest relative-price-spread quintile to 0.623 points in the widest quintile. At 21D and 45D, however, the middle quintiles do not follow a mechanical ordering. Simple portfolios are affected by differences in market regime, ATM level, and date composition.

ATM-IV spread remains positive and statistically significant in the HAC model after controlling for absolute SPY return, past realized volatility, the high-volatility indicator, and tenor fixed effects. The combined evidence supports three conclusions:

- poorer quote quality is associated with greater instability;
- the relationship is not mechanically monotonic in every liquidity portfolio; and
- liquidity does not fully explain the maturity effect.

---

## 8. ATM IV Versus Total Variance

| Tenor | Median \(|\Delta ATMIV|\) | Median \(|\Delta w|\) | Median relative \(|\Delta w|/w_{t-1}\) |
|---:|---:|---:|---:|
| 21D | 0.765 vol pts | 0.000144 | 13.12% |
| 45D | 0.625 vol pts | 0.000271 | 10.55% |
| 90D | 0.503 vol pts | 0.000437 | 6.83% |
| 150D | 0.450 vol pts | 0.000675 | 5.61% |

The answer depends on scale:

- absolute annualized ATM-IV changes decline with maturity;
- absolute total-variance changes rise with maturity because total variance mechanically scales with \(T\); and
- relative total-variance changes preserve the finding that short maturities are less stable.

There is no scale-free answer to whether ATM IV or total variance is more stable. Raw absolute total variance reverses the ATM-IV ranking, while relative total variance retains it. This supports pre-registered Hypothesis 7.

---

## 9. Regression Results

### 9.1 Contemporaneous HAC model

The model uses 12,685 observations and has \(R^2=0.537\). The 21D tenor is the reference category.

| Variable | Coefficient | HAC SE | p-value | Interpretation |
|---|---:|---:|---:|---|
| 45D fixed effect | -0.00264 | 0.00089 | 0.0031 | Approximately 0.264 vol pts below 21D |
| 90D fixed effect | -0.00477 | 0.00177 | 0.0069 | Approximately 0.477 vol pts below 21D |
| 150D fixed effect | -0.00657 | 0.00240 | 0.0061 | Approximately 0.657 vol pts below 21D |
| ATM-IV spread | 0.482 | 0.136 | 0.00040 | Positive quote-uncertainty association |
| Absolute SPY return | 1.019 | 0.0617 | <10⁻⁶⁰ | Dominant contemporaneous correlate |
| High/extreme regime | 0.00033 | 0.00065 | 0.614 | Not significant after controls |
| Log DTE | 0.00018 | 0.00126 | 0.886 | Not significant with tenor fixed effects |
| Past realized volatility | -0.00016 | 0.00297 | 0.958 | Conditionally insignificant |

The negative and significant tenor fixed effects support greater short-dated instability. Absolute underlying return is the strongest contemporaneous correlate. Descriptive regime differences are large, but the high/extreme indicator is not significant after controlling for the same-day return, quote spread, and tenor. The regime tables should therefore not be treated as independent causal effects.

### 9.2 Next-observation quote-uncertainty model

The next-observation model uses 12,683 observations and has \(R^2=0.204\). The ATM-IV-spread coefficient is 0.701 (p=0.00023), the absolute-return coefficient is 0.305 (p<0.0001), and the past-realized-volatility coefficient is 0.0233 (p<10⁻¹⁴). The 45D, 90D, and 150D fixed effects remain significantly negative relative to 21D.

Today's wider ATM quote interval is associated with a larger ATM estimate change at the next comparable observation. The model has limited predictive explanatory power and does not establish causality.

---

## 10. Vendor IV and Carry Sensitivity

The three panels share 12,808 date-tenor keys. Of these, 12,712 have the same finite previous observation under all three specifications. The selected expiration is identical for 99.992% of common keys.

### 10.1 Three-way paired stability

| Specification | 21D | 45D | 90D | 150D | Ranking, most stable first |
|---|---:|---:|---:|---:|---|
| Vendor-IV replication | 0.765 | 0.640 | 0.521 | 0.448 | 150, 90, 45, 21 |
| NCX Treasury + projected distributions | 0.765 | 0.625 | 0.503 | 0.450 | 150, 90, 45, 21 |
| NCX Treasury + trailing dividend yield | 0.883 | 0.768 | 0.512 | 0.413 | 150, 90, 45, 21 |

Entries are median daily absolute ATM-IV changes in volatility points.

Vendor and baseline ATM-IV level correlations range from 0.992 to 0.996. Vendor median levels are approximately 0.295 to 0.463 volatility points below baseline. Aggregate stability is close, although individual absolute-move correlations range only from 0.746 to 0.926. Vendor and NCX estimates can therefore disagree materially on particular dates even when their aggregate maturity ranking is identical.

Trailing-yield and baseline level correlations range from 0.995 to 0.998. The alternative does not change the ranking, but it changes the magnitude:

- 21D median instability increases by 0.118 volatility points, or approximately 15.5%;
- 45D increases by 0.143 points, or approximately 22.9%;
- 90D increases by 0.010 points, or approximately 1.9%; and
- 150D decreases by 0.038 points, or approximately 8.3%.

The maturity ordering is not a carry artifact, but the magnitude of the short- and intermediate-tenor effect is materially carry-sensitive.

![Figure 5 — Carry-specification comparison](carry_stability_comparison.png)

---

## 11. Assessment of Pre-Registered Hypotheses

| Hypothesis | Assessment | Evidence and qualification |
|---|---|---|
| H1: Short-dated ATM IV changes more than long-dated ATM IV | **Supported** | Nearest-tenor, fixed-expiry, vendor-IV, and both NCX carry specifications agree |
| H2: Wider ATM-IV spreads predict larger next changes | **Association supported** | Spearman correlations of 0.20–0.23; HAC coefficient 0.701, p=0.00023; not causal |
| H3: ATM stability deteriorates in high-volatility regimes | **Descriptively supported; weaker conditional evidence** | Extreme/low differences are large, but the controlled high-regime coefficient is insignificant |
| H7: ATM total variance and ATM IV may rank stability differently | **Supported** | Absolute \(|\Delta w|\) reverses the ranking; relative \(|\Delta w|/w\) retains short-dated instability |
| H8: Nearest tenor is preferable for daily analysis | **Partially supported; final test incomplete** | Fixed-expiry and nearest-tenor directions agree; Stage 3.3 constant maturity is unavailable |

Hypotheses 4 through 6 concern cross-underlying comparisons and belong to Research 001B. They are not tested in this report.

---

## 12. Robustness Summary

Completed formal robustness analyses include:

1. vendor IV versus raw-price NCX IV;
2. Treasury projected-distribution baseline versus Treasury trailing-yield alternative;
3. retained bid, midpoint, and ask ATM estimates;
4. nearest-tenor versus fixed-expiry DTE bins;
5. absolute versus relative ATM-IV changes;
6. ATM IV versus total variance;
7. calendar periods versus pooled-IV-quantile regimes; and
8. descriptive and HAC-regression evidence on quote uncertainty.

Constructed diagnostics that have not been promoted to full-chain NCX reconstructions include:

- flat DGS3MO with projected distributions;
- flat SOFR with projected distributions, available only from April 3, 2018;
- realized future distribution amounts, which contain look-ahead and are diagnostic only; and
- option-implied forwards.

Items not yet completed or lacking sufficient observations include:

- true 30D, 60D, and 90D constant-maturity panels;
- a meaningful observed-versus-interpolated ATM comparison, because only eight baseline ATM records are exact observations;
- a full historical OIS or repo financing curve; and
- a point-in-time archive of historical forward-dividend forecasts and announcement dates.

---

## 13. Data Quality and Limitations

1. **Kaggle provenance.** Kaggle is a distribution platform. Original source, snapshot timing, and field definitions rely materially on the uploader's frozen description.
2. **Vendor-model opacity.** The vendor's IV and Greek assumptions are incomplete. Vendor values are replication and disagreement benchmarks, not ground truth.
3. **Treasury financing proxy.** Treasury constant-maturity yields are not SPY option financing, repo, or OIS rates. Treating them as continuously compounded zero-rate proxies is an explicit approximation.
4. **Dividend timing.** The baseline avoids future cash amounts but uses the ultimately realized historical ex-date calendar. The trailing-yield alternative removes discrete timing but introduces smoothing error.
5. **American exercise.** SPY options are American-style. Early exercise and discrete distributions may affect both IV inversion and simple parity diagnostics.
6. **EOD synchronization.** The uploader claims a 4:00 p.m. snapshot, but underlying last, option quotes, and vendor analytics may not be perfectly synchronized.
7. **Quote quality.** The raw data contain 33,460 crossed-market rows, 11,727 missing-bid rows, 11,727 missing-ask rows, and 106,588 non-positive asks. Explicit cleaning and attrition records are retained.
8. **Eight no-quote dates.** January 27 through February 5, 2010 have no usable two-sided bid/ask quotes and cannot be reconstructed from raw prices.
9. **ATM interpolation.** Most ATM values are total-variance interpolations rather than exact observed-strike values. Two trailing-yield expiry records have bid/mid ordering exceptions.
10. **Endogenous regimes.** Regimes are based on pooled sample ATM-IV quantiles and are descriptive, not external stress instruments.
11. **Nearest-expiry rollover.** Target-tenor expiries roll over. Fixed-expiry results support the direction, but true constant maturity is not yet available.
12. **Inference.** HAC errors address limited serial correlation but do not resolve generated-regressor concerns, overlapping-tenor dependence, multiple testing, or causal identification.
13. **External validity.** The study concerns SPY only and does not represent all ETFs, single stocks, or the broader US options market.

---

## 14. Reproducibility

The research archive includes:

- frozen Kaggle files, version metadata, README snapshot, sizes, and SHA-256 hashes;
- frozen FRED and State Street source files with SHA-256 hashes;
- immutable configuration and configuration hash;
- expiry, tenor, return, and carry Parquet panels;
- sample attrition, daily exclusions, audit failures, and numerical validation;
- run manifests, logical panel hashes, and output hashes for each specification; and
- deterministic daily checkpoints that support safe resumption.

The complete non-large test suite reports **458 passed and 1 deselected**. The deselected test carries the project's default `large` marker and is not a failed Research 001 test.

Principal reproducibility artifacts are:

- `spy_2010_2023_ncx_baseline/atm_expiry_panel.parquet`;
- `spy_2010_2023_ncx_baseline/atm_tenor_panel.parquet`;
- `spy_2010_2023_ncx_trailing_dividend/atm_expiry_panel.parquet`;
- `spy_2010_2023_ncx_trailing_dividend/atm_tenor_panel.parquet`;
- `spy_2010_2023_carry_comparison/carry_specification_comparison.csv`;
- `spy_2010_2023_carry_comparison/paired_carry_differences.csv`; and
- `historical_carry/carry_source_manifest.json`.

---

## 15. Conclusion

SPY ATM implied volatility is not uniformly stable across dates and maturities. The 2010–2023 evidence supports seven central conclusions:

1. Typical and tail ATM-IV changes are materially larger at short maturities.
2. The maturity ranking survives fixed-expiry, nearest-tenor, vendor-IV, and two historical-carry NCX specifications.
3. Market stress reduces stability across the full term structure, with the greatest amplification at the front end.
4. Bid–ask IV uncertainty is related to observed instability but cannot explain most daily changes.
5. Liquidity effects are not monotonic in simple portfolios, although wider ATM-IV spreads remain positively related to instability in conditional regressions.
6. Total-variance conclusions depend on whether changes are measured in absolute or relative terms.
7. Carry specification does not change the qualitative maturity result, but it materially affects the magnitude of short- and intermediate-tenor instability.

The most accurate one-sentence conclusion is:

> **SPY ATM volatility is not uniformly stable: stability improves with maturity, deteriorates sharply in stressed markets, and remains qualitatively robust—but not quantitatively invariant—across vendor and historical-carry specifications.**

---

## References and Source Records

1. Frozen Kaggle provenance: `data/raw/kaggle/spy_options_2010_2023/dataset_manifest.json`.
2. Federal Reserve Economic Data, Treasury Constant Maturity Rate series: <https://fred.stlouisfed.org/data/DGS1MO>.
3. Federal Reserve Economic Data, Secured Overnight Financing Rate: <https://fred.stlouisfed.org/series/SOFR>.
4. State Street Global Advisors, ETF Dividend Distributions: <https://www.ssga.com/us/en/intermediary/resources/documents/etf-dividend-distributions>.
5. Historical carry methodology: `outputs/historical_carry/historical_carry_methodology.md`.
6. Baseline run manifest: `outputs/spy_2010_2023_ncx_baseline/run_manifest.json`.
7. Carry-comparison manifest: `outputs/spy_2010_2023_carry_comparison/comparison_manifest.json`.
