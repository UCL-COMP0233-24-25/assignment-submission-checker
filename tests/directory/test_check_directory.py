from pathlib import Path
from typing import Optional

import pytest

from assignment_submission_checker.directory import Directory
from assignment_submission_checker.utils import AssignmentCheckerError


def test_check_directory_fatal_cases() -> None:
    """
    Check that FATAL errors are recorded in each of the
    """
