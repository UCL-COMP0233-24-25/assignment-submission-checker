import json
from pathlib import Path
from typing import Dict, List

import pytest

from assignment_submission_checker.directory import Directory


@pytest.fixture
def A1_2024_2025(DATA_DIR: Path) -> Directory:
    with open(DATA_DIR / "2024-25-01.json") as f:
        loaded_json = json.load(f)
    return Directory("structure", loaded_json["structure"], parent=None)


@pytest.fixture
def A1_2024_2025_folder_structure_all_optional() -> Dict[str, List[str | Dict]]:
    return {
        "depot_locations_test_student": [
            "country.py",
            "execution_times.py",
            "test_country.py",
            "utilities.py",
            "deciding_depot_locations.ipynb",
            "plotting_utilities.py",
            {
                "report": [
                    "report.md",
                    "nna_execution_times.png",
                    "AIUsage.md",
                    "Feedback.md",
                ]
            },
            {
                "data": [
                    "locations.csv",
                    "custom_dataset.csv",
                ]
            },
        ]
    }


@pytest.fixture
def A1_2024_2025_folder_structure_no_optional() -> Dict[str, List[str | Dict]]:
    return {
        "depot_locations_test_student": [
            "country.py",
            "execution_times.py",
            "test_country.py",
            "utilities.py",
            {
                "report": [
                    "report.md",
                    "nna_execution_times.png",
                ]
            },
        ]
    }


@pytest.fixture
def A1_2024_2025_git_specs() -> Dict[str, str]:
    """
    rootdir: tmp_path / depot_locations_test_student
    commit: Commit to main by default.
    checkout: Create a random WIP branch for some variety.
    """
    return {"checkout": "work-in-progress", "rootdir": "depot_locations_test_student"}


@pytest.mark.parametrize(
    ["make_folder_structure", "setup_folder_structure_with_git"],
    [
        pytest.param(
            "A1_2024_2025_folder_structure_all_optional",
            "A1_2024_2025_git_specs",
            id="Assignment 1, 2024-25 [all optional files present]",
        ),
        pytest.param(
            "A1_2024_2025_folder_structure_no_optional",
            "A1_2024_2025_git_specs",
            id="Assignment 1, 2024-25 [no optional files present]",
        ),
    ],
    indirect=["make_folder_structure", "setup_folder_structure_with_git"],
)
def test_on_A1_2024_2025(
    setup_folder_structure_with_git, tmp_path: Path, A1_2024_2025: Directory
) -> None:
    fatal, warnings, information = A1_2024_2025.check_against_directory(
        tmp_path / "depot_locations_test_student"
    )

    assert fatal is None, "Fatal error thrown on an otherwise OK assignment!"
    assert (
        len(warnings) == 1
        and warnings[0] == "Repository was not on the main branch, switching now..."
    ), "Exactly one warning should have been thrown: for the repo being on the wrong branch."
