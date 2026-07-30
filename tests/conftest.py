from pathlib import Path


def pytest_configure() -> None:
    Path(".tmp").mkdir(exist_ok=True)
