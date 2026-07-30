from pathlib import Path
import runpy
import shutil

import pytest


EXAMPLES = (
    "01_build_canonical_snapshot.py",
    "02_ingest_provider_csv.py",
    "03_validate_option_chain.py",
    "04_enrich_option_chain.py",
    "05_clean_option_chain.py",
    "06_diagnose_static_arbitrage.py",
    "07_pandas_interoperability.py",
    "08_write_dataset_snapshot.py",
    "09_end_to_end_pipeline.py",
)
PANDAS_EXAMPLES = {
    "07_pandas_interoperability.py",
    "09_end_to_end_pipeline.py",
}


@pytest.mark.parametrize("filename", EXAMPLES)
def test_market_data_example_runs(filename: str, monkeypatch, tmp_path) -> None:
    if filename in PANDAS_EXAMPLES:
        pytest.importorskip("pandas")
    repo_root = Path(__file__).parents[2]
    output_dir = tmp_path / "examples_output"
    monkeypatch.setenv("NCX_EXAMPLES_OUTPUT_DIR", str(output_dir))
    path = (
        repo_root
        / "examples"
        / "market_data"
        / filename
    )

    try:
        runpy.run_path(str(path), run_name="__main__")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
