import os
from pathlib import Path
from typing import Any, Callable, Literal

import pytest

from assignment_submission_checker.assignment import Assignment

# Path to the data directory with "fake" assignment formats
DATA_DIR = (Path(os.path.abspath(os.path.dirname(__file__))) / "data").resolve()


@pytest.fixture()
def placeholder_assignment(tool: Literal["tar", "zip"] = "tar") -> Assignment:
    """
    Standard template assignment that can be used for testing.

    It assumes the following directory and file structure is needed for the assignment:

    candidate_number/
    - assignment/
    - - .git/
    - - code_file_1.py
    - - code_file_2.py
    - - data/
    - - - data_file_1.dat
    """
    return Assignment(
        "Test assignment object",
        git_root=Path("assignment"),
        archive_tool=tool,
        expected_files=[
            Path("assignment/code_file_1.py"),
            Path("assignment/code_file_2.py"),
            Path("assignment/data/data_file_1.dat"),
        ],
    )
