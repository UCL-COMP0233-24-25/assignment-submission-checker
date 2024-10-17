from pathlib import Path

import pytest

from assignment_submission_checker.assignment import Assignment
from assignment_submission_checker.directory import Directory


def test_from_json(test_data_assignment: Assignment, test_dir_structure: Directory) -> None:
    assert test_data_assignment.year == 2024
    assert test_data_assignment.assignment_id == "01"

    assert (
        test_data_assignment.directory_structure == test_dir_structure
    ), "Directory structure read in does not match expected."


@pytest.fixture
def move_into_zip(setup_folder_structure) -> None:
    pass


# Test for extraction (use tempdir fixture....)
def test_extract_to(tmp_path: Path, test_data_assignment: Assignment) -> None:
    test_data_assignment.extract_to()


# Test for check submission return value? Should either be None or an error.
