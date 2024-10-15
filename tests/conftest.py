import json
import os
from pathlib import Path
from typing import Any, Dict, TypeAlias

import pytest

JsonData: TypeAlias = Dict[str, Any]


@pytest.fixture(scope="session")
def DATA_DIR() -> Path:
    return (Path(os.path.abspath(os.path.dirname(__file__))) / "data").resolve()


@pytest.fixture
def test_data_json(DATA_DIR) -> Path:
    return DATA_DIR / "template.json"


@pytest.fixture
def test_data_dict(test_data_json: Path) -> JsonData:
    with open(test_data_json, "r") as f:
        data = json.load(f)
    return data
