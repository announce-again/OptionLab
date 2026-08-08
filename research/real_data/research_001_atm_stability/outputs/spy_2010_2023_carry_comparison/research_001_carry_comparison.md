# Research 001A — historical carry and full-history NCX comparison

## Result

The maturity-stability result survives both NCX carry specifications: 150D is most stable and 21D is least stable in the three-way paired sample. Under the baseline, the 21D median daily absolute ATM-IV change is 1.70× the 150D value.

The largest change in the tenor-level median instability occurs at 45D: the trailing-yield result differs from baseline by +0.1432 vol points (+22.9%). At the individual-move level, the largest median absolute paired difference is 0.3777 vol points. Thus the qualitative maturity ordering is not a carry artifact, but its quantitative magnitude is carry-sensitive, especially at short and intermediate tenors.

## Stability rankings (most stable first)

- `vendor_iv_replication`: [150, 90, 45, 21]
- `ncx_treasury_projected_dividends`: [150, 90, 45, 21]
- `ncx_treasury_trailing_dividend_yield`: [150, 90, 45, 21]

## Paired sample

The three panels share 12,808 underlying-date-tenor keys; 12,712 have the same finite previous observation in all three specifications. The selected expiration is identical on 99.992% of common keys.

## Carry coverage

Treasury projected-distribution and trailing-yield specifications cover 100.000% of expiry rows. The flat-3M Treasury diagnostic covers 100.000%; SOFR begins on 2018-04-03 and covers 57.235%.

## Numerical validation

Both NCX tenor panels have positive risk-free and dividend discount factors and no duplicate keys. Independent bid/mid/ask smile interpolation produces 2 bid/mid/ask ordering exceptions across the two NCX expiry panels; these observations are retained and listed rather than silently repaired.

## Interpretation limits

Treasury constant-maturity yields are investment-yield proxies, not option financing/OIS curves. The projected cash-dividend baseline uses the latest SPY distribution amount known on each quote date and historical ex-date seasonality; the trailing-yield alternative smooths quarterly timing. Option-implied forwards are retained as diagnostics because American exercise and quote noise can contaminate put-call parity.
