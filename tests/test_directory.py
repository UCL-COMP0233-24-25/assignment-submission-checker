from pathlib import Path
from typing import Optional, Set

import pytest

from assignment_submission_checker.directory import Directory
from assignment_submission_checker.utils import AssignmentCheckerError


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
@pytest.mark.parametrize(
    ["file_structure", "folder_to_check", "expected_missing", "expected_unexpected"],
    [
        pytest.param(
            False,
            "repo_name",
            [],
            [],
            id="Good file structure, repo_name",
        ),
        pytest.param(
            True,
            "repo_name",
            ["c2.py"],
            [],
            id="Missing compulsory file, repo_name",
        ),
        pytest.param(
            False,
            "repo_name/report",
            [],
            [],
            id="Good file structure, repo_name/report",
        ),
        pytest.param(
            True,
            "repo_name/report",
            [],
            ["wrong_image.pdf"],
            id="Unexpected .pdf file, repo_name/report",
        ),
        pytest.param(
            False,
            "repo_name/data",
            [],
            [],
            id="Good file structure, repo_name/data",
        ),
        pytest.param(
            True,
            "repo_name/data",
            [],
            ["wrong_format.json"],
            id="Unexpected .json file, repo_name/data",
        ),
    ],
    indirect=["file_structure"],
)
def test_check_files(
    setup_folder_structure,
    tmp_path: Path,
    test_dir_structure: Directory,
    folder_to_check: str,
    expected_missing: Set[str],
    expected_unexpected: Set[str],
) -> None:
    if isinstance(expected_missing, list):
        expected_missing = set(expected_missing)
    if isinstance(expected_unexpected, list):
        expected_unexpected = set(expected_unexpected)

    missing, unexpected = test_dir_structure[folder_to_check].check_files(
        tmp_path / folder_to_check
    )

    assert missing == expected_missing, "Not all missing files were flagged."
    assert unexpected == expected_unexpected, "Not all unexpected files were identified."


@pytest.mark.parametrize(
    ["file_structure", "git_repo_loc", "git_commit_work_to", "git_switch_to", "expected_error"],
    [
        pytest.param(
            False,
            "repo_name",
            None,
            None,
            None,
            id="Repo in correct location",
        ),
        pytest.param(
            False,
            "repo_name/report",
            None,
            None,
            AssignmentCheckerError,
            id="Repo in wrong location",
        ),
        pytest.param(
            False,
            "repo_name",
            "bad_branch",
            "main",
            AssignmentCheckerError,
            id="Work not on main branch",
        ),
        pytest.param(
            False,
            "repo_name",
            "main",
            "on_wrong_branch",
            None,
            id="Git repo on wrong branch, but work is on main.",
        ),
    ],
    indirect=["file_structure"],
)
def test_check_directory(
    setup_submission_folder,
    tmp_path: Path,
    test_dir_structure: Directory,
    git_repo_loc: Optional[str],
    git_commit_work_to: Optional[str],
    git_switch_to: Optional[str],
    expected_error: Optional[Exception],
) -> None:
    if expected_error is not None:
        with pytest.raises(expected_error):
            test_dir_structure.check_against_directory(tmp_path)
    else:
        test_dir_structure.check_against_directory(tmp_path)
        assert (
            test_dir_structure.name == tmp_path.stem
        ), "Variable name was not inherited from folder."
    pass
