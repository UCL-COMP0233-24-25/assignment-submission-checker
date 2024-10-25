from pathlib import Path
from typing import Dict, List

import pytest

from assignment_submission_checker.directory import Directory

# TSTK: There are known bugs here - when dealing with two optional subdirectories that
# can feasibly have the same structure when submitted, the method of assigning
# which folder to which will not give a unique answer, which can result in the
# two folders being labelled as each other.


@pytest.fixture
def directory_structure_for_variable_name_checking() -> Directory:
    return Directory(
        "top-level-folder",
        {
            "variable-name": False,
            "nested-dir-1": {
                "variable-name": "*",
                "compulsory": ["a.py", "b.py"],
            },
            "nested-dir-2": {
                "variable-name": "*",
                "compulsory": ["a.py", "b.py"],
                "data-file-types": ["*.csv"],
            },
            "nested-dir-3": {
                "variable-name": "*",
                "compulsory": ["a.py"],
                "optional": ["b.py"],
            },
            "nested-dir-4": {
                "variable-name": "*",
                "compulsory": ["a.py", "b.py"],
                "data-file-types": ["*.json"],
                "nested-nested-dir-1": {
                    "variable-name": "*nested?",
                    "compulsory": ["data.csv"],
                },
                "nested-nested-dir-2": {
                    "compulsory": ["data.csv"],
                },
            },
            "nested-dir-5": {
                "variable-name": "*",
                "compulsory": ["a.py", "b.py"],
                "data-file-types": ["*.json"],
                "nested-nested-dir-1": {
                    "variable-name": "*nested?",
                    "compulsory": ["data.csv"],
                },
                "nested-nested-dir-2": {
                    "variable-name": "?nested*",
                    "data-file-types": ["*.csv"],
                },
            },
        },
        None,
    )


@pytest.fixture
def file_structure_matching_variable_names() -> Dict[str, List[str | Dict]]:
    return {
        "top-level-folder": [
            {"matches-1": ["a.py", "b.py"]},
            {"matches-2": ["a.py", "b.py", "data_2.csv"]},
            {"matches-3": ["a.py"]},
            {
                "matches-4": [
                    "a.py",
                    "b.py",
                    "alt_data.json",
                    {"sub-nested1": ["data.csv"]},
                    {"nested-nested-dir-2": ["data.csv"]},
                ]
            },
            {
                "matches-5": [
                    "a.py",
                    "b.py",
                    "alt_data.json",
                    {"sub-nested1": ["data.csv"]},
                    {"2nested-sub": ["data.csv"]},
                ]
            },
        ]
    }


@pytest.mark.parametrize(
    ["make_folder_structure"],
    [pytest.param("file_structure_matching_variable_names")],
    indirect=["make_folder_structure"],
)
def test_match_variable_names(
    make_folder_structure,
    tmp_path: Path,
    directory_structure_for_variable_name_checking: Directory,
) -> None:
    a, b = directory_structure_for_variable_name_checking.match_variable_name_subdirs(
        tmp_path / "top-level-folder"
    )

    assert len(b) == 0, "All subdirectories should have been matched!"
    assert len(a) == 5, "All subdirectories should have been matched!"
    for i in range(1, 6):
        assert (
            a[f"matches-{i}"].name
            == directory_structure_for_variable_name_checking[f"nested-dir-{i}"].name
        ), f"Wrong directory matched to matches-{i}."
