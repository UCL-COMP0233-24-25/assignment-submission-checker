from pathlib import Path

import pytest

from assignment_submission_checker.checker import check_archive_name


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
    ), f"check_archive_name({name, c_number} returned {result} but expected {expected_result}.)"
