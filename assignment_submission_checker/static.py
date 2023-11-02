from pathlib import Path

from .assignment import Assignment

# File contains static instances that correspond to assignments issued for COMP0233.

COMP0233_2324_A1 = Assignment(
    name="COMP0233 Assignment 1: Rail Fare Prices (2023/24)",
    git_root=Path("railway"),
    archive_tool="tar",
    expected_files=[
        Path("railway/railway.py"),
        Path("railway/utilities.py"),
        Path("railway/test_railway.py"),
    ],
)
