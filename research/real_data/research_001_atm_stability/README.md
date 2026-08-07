# Research 001 — ATM volatility stability

This package implements the reproducible boundaries for:

- Part A: SPY time-series and maturity stability, 2010–2023.
- Part B: SPY/QQQ/AAPL/NVDA/TSLA comparison, 2020–2022.

Raw Kaggle files are inputs, never outputs. Keep them under `data/raw/kaggle`,
freeze each directory with `dataset_manifest.json`, and write all derived files
under `data/interim`, `data/processed`, or this research package's `outputs`
directory.

## Implemented flow

```text
frozen OptionsDX/Kaggle wide files
  -> call/put long adapter
  -> non-destructive data audit
  -> daily Stage 2 + Stage 3.1 NCX reconstruction
  -> Stage 3.2 bid/mid/ask smiles
  -> expiry-level ATM panel
  -> nearest-tenor panel and daily stability labels
  -> summaries, regressions, plots, report, hashes
```

Stage 3.3 constant-maturity interpolation is intentionally not represented as
complete. Nearest-expiry output remains the baseline until that production
stage exists.

## Freeze provenance

After downloading a Kaggle dataset into its final raw directory:

```powershell
.\.venv\Scripts\python.exe -B -m `
  research.real_data.research_001_atm_stability.download_manifest `
  data\raw\kaggle\spy_options_2010_2023 `
  --slug UPLOADER/DATASET `
  --title "SPY Options EOD Data (2010-2023)" `
  --uploader UPLOADER `
  --version VERSION `
  --claimed-source OptionsDX `
  --license LICENSE `
  --download-timestamp 2026-08-05T12:00:00+00:00 `
  --date-start 2010-01-01 `
  --date-end 2023-12-31
```

The version, uploader, license, source claim, and page/README snapshot must be
copied from the Kaggle page; the code does not guess missing provenance.

## Audit a pilot

```powershell
.\.venv\Scripts\python.exe -B -m `
  research.real_data.research_001_atm_stability.audit `
  --symbol SPY `
  --output-dir data\interim\research_001\spy_pilot `
  data\raw\kaggle\common_uploader\spy_2020_2022\*.parquet
```

The audit writes `standardized_contracts.csv`, `audit_summary.csv`,
`audit_by_date.csv`, `audit_by_expiry.csv`, `audit_failures.csv`,
`schema_report.json`, and `data_quality_report.md`. It does not drop or repair
rows.

## Carry policy

`run_daily_ncx_pipeline` requires an explicit `carry_for_date(date)` callback.
This prevents the pilot zero-rate/zero-dividend diagnostic from being confused
with the baseline rate/dividend enrichment. The callback and its source hashes
belong in `run_manifest.json`.

Install optional research dependencies with:

```powershell
python -m pip install -e ".[research]"
```

Parquet equality is checked on sorted logical records. CSV is deterministic at
the byte level. Raw input hashes, config SHA-256, and output hashes are separate
artifacts.
