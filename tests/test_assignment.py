from pathlib import Path
from typing import Optional

import pytest

from assignment_submission_checker.assignment import Assignment
from assignment_submission_checker.directory import Directory
from assignment_submission_checker.utils import AssignmentCheckerError


def test_from_json(test_data_assignment: Assignment, test_dir_structure: Directory) -> None:
    assert test_data_assignment.year == 2024
    assert test_data_assignment.assignment_id == "01"

    assert (
        test_data_assignment.directory_structure == test_dir_structure
    ), "Directory structure read in does not match expected."


@pytest.mark.parametrize(
    ["file_structure"],
    [pytest.param(False, id="Correct submission format")],
    indirect=["file_structure"],
)
def test_copy_to_tmp_location(setup_folder_structure, tmp_path: Path) -> None:
    extract_to = tmp_path / "extraction"
    Assignment.copy_to_tmp_location(tmp_path, extract_to)

    assert extract_to.exists(), "Extracted files not found at the expected location"


# Test for check submission return value? Should either be None or an error.
@pytest.mark.parametrize(
    [
        "file_structure",
        "git_repo_loc",
        "git_commit_work_to",
        "git_switch_to",
        "expected_exception",
    ],
    [
        pytest.param(False, "repo_name", "main", "main", None, id="Good file structure"),
        pytest.param(
            True, "repo_name", "main", "main", AssignmentCheckerError, id="Bad file structure"
        ),
    ],
    indirect=["file_structure"],
)
def test_check_submission(
    setup_submission_folder,
    tmp_path: Path,
    test_data_assignment: Assignment,
    git_repo_loc: Optional[str],
    git_commit_work_to: Optional[str],
    git_switch_to: Optional[str],
    expected_exception: Optional[Exception],
) -> None:
    if expected_exception is None:
        test_data_assignment.check_submission(tmp_path)
    else:
        with pytest.raises(expected_exception):
            test_data_assignment.check_submission(tmp_path)
