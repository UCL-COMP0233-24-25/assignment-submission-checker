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
            "assignment/code_file_1.py",
            "assignment/code_file_2.py",
            "assignment/data/data_file_1.dat",
        ],
    )


# def extract_then_teardown(data: Path) -> None:
#     """
#     Extract the test data archive to a temporary file,
#     run the test,
#     then purge the temporary directory that was created.
#     """
#     assignment = placeholder_assignment()
#     # Set target data file so that extracted file has expected structure
#     assignment.set_target_archive(data)
#     # Extract
#     assignment.extract_to_temp_dir()
#     # Run test
#     yield
#     # Clean up extracted files
#     assignment.purge_tmp_dir()


# def extract_and_teardown(f: Callable[[Any], Any], assignment: Assignment, data_path: Path):
#     """
#     Decorator for tests that require an assignment submission (or mimicry of such) to be extracted before running.
#     Wraps the original function in the following steps:

#     Extract the test data archive to a temporary file,
#     <Run the initial function passing the additional keyword arguments>
#     then purge the temporary directory that was created.
#     """

#     def wrapper() -> None:
#         # Set target data file so that extracted file has expected structure
#         assignment.set_target_archive(data_path)
#         # Extract
#         assignment.extract_to_temp_dir()
#         # Run test
#         f(assignment=assignment)
#         # Clean up extracted files
#         assignment.purge_tmp_dir()

#         return

#     return wrapper
