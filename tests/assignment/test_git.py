from pathlib import Path
from typing import Literal

import pytest

from assignment_submission_checker.assignment import Assignment

from .. import DATA_DIR
from ._base_testclass import BaseAssignmentTestingClass


class TestGitDetection(BaseAssignmentTestingClass):
    """
    Testing class for the Assignment methods that handle detection of the submission's
    git repository and the state thereof.
    """

    @pytest.mark.parametrize(
        "data_path, repo_should_be_found, repo_should_be_clean",
        [
            pytest.param(
                DATA_DIR / "correct_format.tar.gz",
                True,
                True,
                id="Correct repo setup",
            ),
            pytest.param(DATA_DIR / "no_git_missing_files.tar.gz", False, False, id="No git"),
            pytest.param(DATA_DIR / "dirty_git_extra_files.tar.gz", True, False, id="Dirty HEAD"),
        ],
    )
    def test_git_detection(
        self,
        placeholder_assignment: Assignment,
        repo_should_be_found: bool,
        repo_should_be_clean: bool,
    ):
        """
        Check that:
        - git repositories are searched for in the correct location
        - git repositories can be detected as clean / dirty
        - help messages are returned in the event that there is something that
        needs to be fixed in the assignment.
        """

        # Run the check_for_git_root method
        obtained_result = placeholder_assignment.check_for_git_root()

        # Assert that the results were identical

        # Whether repository was found at the location provided
        assert (
            obtained_result[0] == repo_should_be_found
        ), f"Repository found at expected location: {obtained_result[0]}, but expected {repo_should_be_found}"
        # Whether the repository was clean after extraction
        assert (
            obtained_result[1] == repo_should_be_clean
        ), f"Repository was clean: {obtained_result[1]}, but expected {repo_should_be_clean}"

        # Error message when attempting to find the repository
        if repo_should_be_found:
            assert (
                obtained_result[2] == ""
            ), f"Repository should be found but obtained non-empty error string: {obtained_result[2]}"

            # Error message when determining if the repo was clean
            if repo_should_be_clean:
                assert (
                    obtained_result[3] == ""
                ), f"Repository should be clean but obtained non-empty error string: {obtained_result[3]}"
            else:
                assert (
                    obtained_result[3] != ""
                ), f"Repository should be dirty but obtained an empty error string."
        else:
            assert (
                obtained_result[2] != ""
            ), f"Repository should not be found but obtained empty error string."
