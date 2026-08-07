from __future__ import annotations

from pathlib import Path


def generate_core_figures(tenor_panel, expiry_panel, output_directory: str | Path) -> tuple[Path, ...]:
    """Generate the data-supported core figures; missing optional columns are skipped."""

    plt = _import_pyplot()
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    outputs = []

    summary = tenor_panel.groupby("target_tenor")["absolute_atm_iv_change"].median()
    outputs.append(_bar(plt, summary, root / "figure_01_stability_by_tenor.png", "Target tenor (days)", "Median |Δ ATM IV|"))

    dte = expiry_panel.assign(dte_bin=(expiry_panel["actual_dte"] // 7) * 7).groupby("dte_bin")["absolute_atm_iv_change"].median() if "absolute_atm_iv_change" in expiry_panel else None
    if dte is not None:
        outputs.append(_line(plt, dte, root / "figure_02_stability_by_dte.png", "Actual DTE bin", "Median |Δ ATM IV|"))

    figure, axis = plt.subplots(figsize=(9, 5))
    for tenor, values in tenor_panel.groupby("target_tenor"):
        values = values.sort_values("quote_date")
        rolling = values["absolute_atm_iv_change"].rolling(21, min_periods=10).median()
        axis.plot(values["quote_date"], rolling, label=f"{tenor}D")
    axis.set_ylabel("Rolling 21-observation median |Δ ATM IV|")
    axis.legend()
    outputs.append(_save(figure, root / "figure_03_rolling_stability.png"))

    if {"atm_iv_spread", "absolute_atm_iv_change"}.issubset(tenor_panel.columns):
        figure, axis = plt.subplots(figsize=(7, 5))
        axis.scatter(tenor_panel["atm_iv_spread"], tenor_panel["absolute_atm_iv_change"], s=8, alpha=0.25)
        axis.set_xlabel("ATM IV bid-ask spread")
        axis.set_ylabel("Next/observed |Δ ATM IV|")
        outputs.append(_save(figure, root / "figure_04_quote_uncertainty.png"))

    if "underlying" in tenor_panel and tenor_panel["underlying"].nunique() > 1:
        cross = tenor_panel.groupby("underlying").agg(absolute=("absolute_atm_iv_change", "median"), relative=("relative_atm_iv_change", lambda x: x.abs().median()))
        figure, axis = plt.subplots(figsize=(8, 5))
        cross.plot.bar(ax=axis)
        outputs.append(_save(figure, root / "figure_06_cross_underlying.png"))

    return tuple(outputs)


def _bar(plt, series, path, xlabel, ylabel):
    figure, axis = plt.subplots(figsize=(7, 5))
    series.plot.bar(ax=axis)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    return _save(figure, path)


def _line(plt, series, path, xlabel, ylabel):
    figure, axis = plt.subplots(figsize=(8, 5))
    series.plot(ax=axis)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    return _save(figure, path)


def _save(figure, path):
    figure.tight_layout()
    figure.savefig(path, dpi=160, metadata={"Software": "ncx-derivatives"})
    figure.clear()
    return path


def _import_pyplot():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError("Research 001 plots require matplotlib; install the research extra") from error
    return plt
