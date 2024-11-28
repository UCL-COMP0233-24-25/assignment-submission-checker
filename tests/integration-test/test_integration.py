"""
Runs an integration test that can be used when debugging.

To configure for local development:

- Create a fixture that returns a dictionary defining the keyword arguments that are passed to `cli_main`.
- Run the `test_integration` test, parametrising the `args` variable with your fixture name.
"""

import os
from pathlib import Path
from typing import Dict

import pytest

from assignment_submission_checker.cli_main import main

THIS_DIR = Path(os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture
def default_args() -> Dict[str, str | Path]:
    """
    The default arguments, testing a local set of assignment specs against a locally-created assignment.
    """
    return {
        "assignment_lookup": None,
        "github_clone_url": None,
        "ignore_unexpected_files": ["report-test/fig2-unexpected.png", "*.csv"],
        "local_specs": (THIS_DIR / "inputs" / "specs" / "specs.json").resolve(),
        "submission": (THIS_DIR / "inputs" / "submission").resolve(),
    }


@pytest.mark.parametrize(
    ["args"],
    [
        pytest.param(
            "default_args",
            id="Run with default args",
        )
    ],
)
def test_integration(args: str, request) -> None:
    """
    Runs `cli_main:main` using developer-defined inputs.
    Running in debug mode will respect breakpoints placed in the codebase.
    """
    if isinstance(args, str):
        args = request.getfixturevalue(args)

    got_text = main(**args)

    print(got_text)  # Breakpoints can be placed here to inspect the output
