# Historical carry enrichment

## Risk-free curve

The baseline linearly interpolates DGS1MO, DGS3MO, DGS6MO, DGS1, and DGS2 yields in maturity, with flat endpoint extrapolation, then uses `D_r(t,T)=exp(-r(t,T)T)`. Treasury constant-maturity yields are investment-basis market yields, not option-financing zero rates; the construction is a proxy.

The robustness set contains a flat DGS3MO curve and a flat SOFR diagnostic where SOFR exists. The SOFR diagnostic is not represented as a term OIS curve.

## Dividends

The baseline uses State Street SPY quarterly ex-dates. Each future payment is projected using the most recent cash distribution known by the quote date. Its present value is converted to an equivalent dividend discount factor `(S-PV(dividends))/S`, which preserves quarterly timing without using future amounts.

Alternative specifications use trailing-12-month cash yield and realized future cash distributions. The realized schedule contains look-ahead and is diagnostic only.

## Option-implied forward

A put-call-parity forward is calculated from paired call/put midpoints near spot. SPY options are American, so early exercise and quote noise make this a diagnostic rather than a carry input.
