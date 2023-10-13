from pathlib import Path

from .assignment import Assignment

# File contains static instances that correspond to assignments issued for COMP0233.

COMP0233_2324_A1 = Assignment(
    name="COMP0233 Assignment 1: Rail Fare Prices (2023/24)",
    git_root=Path("rail_network"),
    archive_tool="tar",
    expected_files=[
        "rail_network/railway.py",
        "rail_network/utilities.py",
        "rail_network/test_rail_network.py",
    ],
)
