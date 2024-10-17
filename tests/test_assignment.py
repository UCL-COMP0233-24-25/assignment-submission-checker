from pathlib import Path
from shutil import make_archive, move

import pytest

from assignment_submission_checker.assignment import Assignment
from assignment_submission_checker.directory import Directory


def test_from_json(test_data_assignment: Assignment, test_dir_structure: Directory) -> None:
    assert test_data_assignment.year == 2024
    assert test_data_assignment.assignment_id == "01"

    assert (
        test_data_assignment.directory_structure == test_dir_structure
    ), "Directory structure read in does not match expected."


@pytest.fixture(scope="function")
def move_into_zip(setup_folder_structure, tmp_path: Path, request) -> Path:
    temp_zone_to_compress = tmp_path / "to_compress"
    temp_zone_to_compress.mkdir(exist_ok=True)

    move(tmp_path / "repo_name", temp_zone_to_compress)

    given_name = tmp_path / "archive"
    make_archive(given_name, request.param, root_dir=temp_zone_to_compress)

    move(temp_zone_to_compress / "repo_name", tmp_path)
    temp_zone_to_compress.rmdir()

    return f"{given_name}.{request.param}"


@pytest.mark.parametrize(
    ["file_structure", "move_into_zip"],
    [pytest.param(False, "zip", id="zip archive")],
    indirect=["file_structure", "move_into_zip"],
)
def test_extract_to(tmp_path: Path, move_into_zip: str) -> None:
    extract_to = tmp_path / "extraction"
    Assignment.extract_to(move_into_zip, extract_to)

    assert extract_to.exists(), "Extracted files not found at the expected location"


# Test for check submission return value? Should either be None or an error.
def test_check_submission() -> None:
    pass
