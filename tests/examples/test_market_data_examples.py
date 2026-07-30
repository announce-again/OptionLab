from pathlib import Path
import runpy

import pytest


EXAMPLES = (
    "build_canonical_snapshot.py",
    "ingest_and_validate_csv.py",
    "enrich_option_chain.py",
    "clean_option_chain.py",
)


@pytest.mark.parametrize("filename", EXAMPLES)
def test_market_data_example_runs(filename: str) -> None:
    path = (
        Path(__file__).parents[2]
        / "examples"
        / "market_data"
        / filename
    )

    runpy.run_path(str(path), run_name="__main__")
