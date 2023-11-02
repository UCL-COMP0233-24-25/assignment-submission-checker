from pathlib import Path
from typing import List

import pytest

from assignment_submission_checker.assignment import Assignment

from .. import DATA_DIR
from ._base_testclass import BaseAssignmentTestingClass


class TestFileFinder(BaseAssignmentTestingClass):
    """ """

    @pytest.mark.parametrize(
        "data_path, expected_missing, expected_extra",
        [
            pytest.param(DATA_DIR / "correct_format.tar.gz", [], [], id="Correct submission"),
            pytest.param(
                DATA_DIR / "no_git_missing_files.tar.gz",
                [Path("assignment/code_file_2.py")],
                [],
                id="Missing files",
            ),
            pytest.param(
                DATA_DIR / "dirty_git_extra_files.tar.gz",
                [],
                [
                    Path("assignment/README.md"),
                    Path("assignment/data/custom_data_file.dat"),
                ],
                id="Extra files",
            ),
        ],
    )
    def test_search_for_missing_files(
        self,
        placeholder_assignment: Assignment,
        expected_missing: List[Path],
        expected_extra: List[Path],
    ) -> None:
        """ """
        # Sort input lists just so that comparisons are easier
        expected_missing = sorted(expected_missing)
        expected_extra = sorted(expected_extra)

        # Use the method to retrieve the list of files that were not found, and not expected
        not_found, extra_files = placeholder_assignment.search_for_missing_files()

        # Check that outputs have been returned sorted
        assert not_found == sorted(not_found), f"List of missing files was not sorted: {not_found}"
        assert extra_files == sorted(
            extra_files
        ), f"List of extra files was not sorted: {extra_files}"

        # Check that the method has performed as expected in this case
        # Files that were not found
        assert (
            not_found == expected_missing
        ), f"Did not detect the expected list of missing files.\nGot: {not_found},\nExp: {expected_missing}"
        # Files that were not expected to be present
        assert (
            extra_files == expected_extra
        ), f"Did not detect the expected list of extra files.\nGot: {extra_files},\nExp: {expected_extra}"
