from pathlib import Path
from typing import Literal

import pytest

from assignment_submission_checker.assignment import Assignment


class BaseAssignmentTestingClass:
    """
    Base class that provides a framework for testing the Assignment class.
    By inheriting from this class, other unit tests for methods of the
    Assignment class don't have to worry about setup nor redefining a fixture
    to use.

    This class defines a fixture Assignment (placeholder_assignment) that can
    be used whilst testing. This placeholder assignment assumes the following
    directory structure:

    candidate_number/
    - assignment/
    - - .git/
    - - code_file_1.py
    - - code_file_2.py
    - - data/
    - - - data_file_1.dat

    The class also defines a fixture that automatically wraps any tests that are
    defined. extract_run_teardown can be passed a data_path parameter and will
    automatically set the placeholder_assignment's target archive to the path
    provided, extract it, run the wrapped test, and then handle removal of the
    extracted files (regardless of test result).
    """

    @pytest.fixture(scope="class")
    def placeholder_assignment(self, tool: Literal["tar", "zip"] = "tar") -> Assignment:
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

    @pytest.fixture(
        autouse=True
    )  # Refactor this into a base class, along with the placeholder fixture above, then subclass?
    @pytest.mark.parametrize("tool", ["tar"])
    def extract_run_teardown(self, placeholder_assignment: Assignment, data_path: Path) -> None:
        """
        Wrap a test method in the following manner:

        - Set the placeholder_assignment's target_archive to the data_path provided.
        - Extract the target_archive
        - Run the wrapped test in this context
        - Remove the extracted files (regardless of test result)
        """
        # Set the target assignment to that which was passed in
        placeholder_assignment.set_target_archive(data_path)
        # Extract the target directory to a temporary location
        placeholder_assignment.extract_to_temp_dir()
        # Run the wrapped test
        yield
        # Remove the temporary directory that was created
        placeholder_assignment.purge_tmp_dir()
