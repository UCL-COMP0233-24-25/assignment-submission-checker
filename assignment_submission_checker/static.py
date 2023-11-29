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

COMP0233_2324_A2 = Assignment(
    name="COMP0233 Assignment 2: Planning Journeys with Service Disruptions (2023/24)",
    git_root=Path("repository"),
    archive_tool="tar",
    group_assignment=True,
    expected_files=[
        Path("efficiency/distant_neighbours_times.md"),
        Path("efficiency/distant_neighbours_plot.png"),
        Path("efficiency/distant_neighbours_efficiency.py"),
        Path("github_use/issues.png"),
        Path("github_use/pr.png"),
        Path("github_use/pr_link.txt"),
    ],
)
