from pathlib import Path
from typing import Dict, Optional, Set

import git
import pytest
from conftest import JsonData

from assignment_submission_checker.directory import Directory
from assignment_submission_checker.git_utils import switch_if_safe
from assignment_submission_checker.utils import AssignmentCheckerError


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


@pytest.fixture
def file_structure(request) -> Dict[str, str]:
    """
    Creates a file structure consistent with the template.json assignment definition.

    If the request.param is True, then the file structure created will be incorrect in the
    following ways:

    - "repo_name/c2.py" will not be present, but is compulsory.
    - "repo_name/report/wrong_image.pdf" will be present, but is not expected.
    - "repo_name/data/wrong_format.json" will be present, but is not expected.
    """
    if request.param:
        return {
            "c1.py": "import json\n",
            "report/report.md": "# My Report\n",
            "report/plot.png": "funny_cat_gif",
            "report/wrong_image.pdf": "content",
            "report/AIUsage.md": "# AI Usage File\n",
            "data/custom_data.csv": "forename,surname\nWill,Graham",
            "data/wrong_format.json": "{'foo': 'bar'}",
        }
    else:
        return {
            "c1.py": "import json\n",
            "c2.py": "from typing import Any\n",
            "report/report.md": "# My Report\n",
            "report/plot.png": "funny_cat_gif",
            "report/AIUsage.md": "# AI Usage File\n",
            "data/custom_data.csv": "forename,surname\nWill,Graham",
        }


@pytest.fixture
def setup_folder_structure(tmp_path: Path, file_structure: Dict[str, str]):
    """
    A file structure that - besides a missing GIT repo - is compatible with
    the template.json assignment structure defined in the tests/data folder.
    """
    repo_folder = tmp_path / "repo_name"
    data_folder = repo_folder / "data"
    report_folder = repo_folder / "report"

    # Create folder structure
    repo_folder.mkdir(parents=False, exist_ok=True)
    data_folder.mkdir(parents=True, exist_ok=True)
    report_folder.mkdir(parents=True, exist_ok=True)

    # Populate with files
    for file, content in file_structure.items():
        with open(repo_folder / file, "w") as f:
            f.write(content)

    # Run test
    yield


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
    setup_folder_structure,
    tmp_path: Path,
    test_dir_structure: Directory,
    git_repo_loc: Optional[str],
    git_commit_work_to: Optional[str],
    git_switch_to: Optional[str],
    expected_error: Optional[Exception],
) -> None:
    if git_repo_loc is not None:
        # Setup the git repo in the target folder
        if git_commit_work_to is None:
            git_commit_work_to = "main"
        if git_switch_to is None:
            git_switch_to = "main"

        repo_dir = tmp_path / git_repo_loc
        if not repo_dir.is_dir():
            raise RuntimeError("Target git folder needs to exist!")

        # Create initial commit, then revert it to not affect the test structure
        repo = git.Repo.init(repo_dir)
        if repo.active_branch.name != "main":
            repo.git.branch("-m", "main")
        repo.git.commit("--allow-empty", "-m", "Initial commit to main")

        # Switch to the branch that the work needs to be committed to
        switch_if_safe(repo, git_commit_work_to, create=True)

        # Commit all work to this branch
        repo.git.add(".")
        repo.git.commit("-m", "Commit all work.")

        # Switch to the branch that we want the repo left on
        switch_if_safe(repo, git_switch_to, True)

    if expected_error is not None:
        with pytest.raises(expected_error):
            test_dir_structure.check_against_directory(tmp_path)
    else:
        test_dir_structure.check_against_directory(tmp_path)
        assert (
            test_dir_structure.name == tmp_path.stem
        ), "Variable name was not inherited from folder."
    pass
