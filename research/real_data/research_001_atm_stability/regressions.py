from __future__ import annotations

from research.real_data.common.regression import fit_clustered_ols, fit_hac_ols


def run_spy_regression(panel, *, max_lags: int = 5):
    data = _prepare(panel)
    formula = (
        "absolute_atm_iv_change ~ log_dte + atm_iv_spread + "
        "absolute_underlying_return + past_realized_volatility + "
        "high_vol_regime + C(target_tenor)"
    )
    return fit_hac_ols(data, formula=formula, max_lags=max_lags)


def run_quote_uncertainty_regression(panel, *, max_lags: int = 5):
    data = _prepare(panel).sort_values(["underlying", "target_tenor", "quote_date"])
    group = data.groupby(["underlying", "target_tenor"], sort=False)
    data["next_absolute_atm_iv_change"] = group["absolute_atm_iv_change"].shift(-1)
    formula = (
        "next_absolute_atm_iv_change ~ atm_iv_spread + "
        "absolute_underlying_return + past_realized_volatility + C(target_tenor)"
    )
    return fit_hac_ols(data, formula=formula, max_lags=max_lags)


def run_cross_underlying_regression(panel):
    data = _prepare(panel)
    formula = (
        "absolute_atm_iv_change ~ log_dte + median_relative_price_spread + "
        "atm_iv_spread + absolute_underlying_return + C(underlying) + "
        "C(quote_date) + C(target_tenor)"
    )
    return fit_clustered_ols(data, formula=formula, cluster_column="underlying")


def _prepare(panel):
    import numpy as np

    data = panel.copy()
    data["log_dte"] = np.log(data["actual_dte"])
    if "high_vol_regime" not in data:
        if "market_regime" in data:
            data["high_vol_regime"] = data["market_regime"].isin(["high", "extreme"]).astype(int)
        else:
            data["high_vol_regime"] = 0
    return data
