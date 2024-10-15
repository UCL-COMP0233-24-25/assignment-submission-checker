from pathlib import Path

import pytest
from conftest import JsonData

from assignment_submission_checker.directory import Directory


@pytest.fixture
def test_dir_structure(test_data_dict: JsonData) -> Directory:
    return Directory("root", test_data_dict["structure"], parent=None)


def test_init(test_dir_structure: Directory):
    placeholder_name = "root"
    path_to_repo = "repo_name"
    path_to_data = "repo_name/data"

    # Manual validation of what was read in
    assert test_dir_structure.name == placeholder_name
    assert test_dir_structure.parent is None
    assert not test_dir_structure.compulsory
    assert not test_dir_structure.optional
    assert not test_dir_structure.is_optional
    assert not test_dir_structure.data_file_patterns
    assert not test_dir_structure.is_data_dir
    assert test_dir_structure.variable_name
    assert test_dir_structure.path_from_root == Path(".")
    assert len(test_dir_structure.subdirs) == 1

    # Validate that we can fetch children via reference
    repo_directory = test_dir_structure[path_to_repo]

    assert repo_directory.git_root
    assert {"c1.py", "c2.py"} == set(repo_directory.compulsory)
    assert {"notebook.ipynb", "provided_code.py"} == set(repo_directory.optional)
    assert repo_directory.path_from_root == Path(path_to_repo)
    assert len(repo_directory.subdirs) == 2
    assert repo_directory.parent is test_dir_structure

    # Validate that we can fetch children via path ref
    data_dir = test_dir_structure[path_to_data]

    assert not data_dir.is_optional, "No compulsory files should imply directory is optional"
    assert data_dir.is_data_dir
    assert data_dir.path_from_root == Path(path_to_data)
    assert data_dir.parent is repo_directory


def test_traverse(test_dir_structure: Directory) -> None:
    expected_order = [
        "root",
        "repo_name",
        "data",
        "report",
    ]

    for expected_name, dir in zip(expected_order, test_dir_structure):
        assert expected_name == dir.name, "Out-of-order-iteration through file structure!"


### Need to check compare against file structures...
