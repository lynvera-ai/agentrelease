import pytest


@pytest.fixture
def policy():
    return {
        "schema_version": 1,
        "id": "synthetic-release",
        "tests": [
            {
                "id": "quality",
                "metrics": [{"name": "accuracy", "operator": ">=", "threshold": 0.9}],
            },
            {"id": "boundary"},
        ],
    }


@pytest.fixture
def evidence():
    return {
        "schema_version": 1,
        "tests": [
            {"id": "quality", "status": "passed", "metrics": {"accuracy": 0.95}},
            {"id": "boundary", "status": "passed"},
        ],
    }
