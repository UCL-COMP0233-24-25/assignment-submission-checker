from pathlib import Path

import pytest

from assignment_submission_checker.checker import (
    check_archive_name,
    check_archive_name_group,
)


@pytest.mark.parametrize(
    "name, c_number, expected_result",
    [
        pytest.param(
            Path("/foo/bar/12345678.zip"),
            "12345678",
            True,
            id="Correct candidate number passed explicitly",
        ),
        pytest.param(
            Path("/foo/bar/12345678.zip"),
            None,
            True,
            id="Valid candidate number, not passed explicitly",
        ),
        pytest.param(
            Path("/foo/bar/n0tnmb3r.tar.gz"),
            None,
            False,
            id="Candidate number is not a numeric string",
        ),
        pytest.param(
            Path("/foo/bar/0123456789.zip"),
            None,
            False,
            id="Too many characters for a candidate number",
        ),
        pytest.param(
            Path("/foo/bar/12345678.tar.gz"),
            "87654321",
            False,
            id="Valid, but incorrect, candidate number",
        ),
    ],
)
def test_check_archive_name(name: Path, c_number: str, expected_result: bool) -> None:
    """
    Check that archive names are correctly parsed and return the expected results.
    """
    result = check_archive_name(name, expected_candidate_number=c_number)
    assert (
        expected_result == result
    ), f"check_archive_name({name, c_number}) returned {result} but expected {expected_result}."


@pytest.mark.parametrize(
    "name, g_number, expected_result",
    [
        pytest.param(
            Path("/foo/bar/working_group_01.zip"),
            "01",
            True,
            id="Correct working group format, attentive c_number",
        ),
        pytest.param(
            Path("/foo/bar/working_group_01.tar.gz"),
            "1",
            True,
            id="Correct submission format, lazy c_number",
        ),
        pytest.param(
            Path("/foo/bar/working_group_01.zip"),
            "02",
            False,
            id="Correct submission format, bad c_number",
        ),
        pytest.param(
            Path("/foo/bar/working_group_01.zip"),
            None,
            True,
            id="Correct submission format, no c_number to compare to",
        ),
        pytest.param(
            Path("/foo/bar/working_group_flibble.tar.gz"),
            None,
            True,
            id="Correct submission format with unorthodox group number will be accepted",
        ),
        pytest.param(
            Path("/foo/bar/working_group_1.zip"),
            None,
            False,
            id="Bad submission format for numeric-only candidate number",
        ),
        pytest.param(Path("/foo/bar/i_work_alone_01.tar.gz"), "01", False, id="Bad archive name"),
        pytest.param(
            Path("/foo/bar/working_group__01.zip"),
            "01",
            False,
            id="Bad submission format, sneaking in extra underscores",
        ),
    ],
)
def test_check_archive_name_group(name: Path, g_number: str, expected_result: bool) -> None:
    """
    Check that archive names are correctly parsed and return the expected results, for group assignments.
    """
    result = check_archive_name_group(name, expected_group_number=g_number)
    assert (
        expected_result == result
    ), f"check_archive_group_name({name, g_number}) returned {result} but expected {expected_result}."
