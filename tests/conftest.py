import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, TypeAlias

import git
import pytest

from assignment_submission_checker.assignment import Assignment
from assignment_submission_checker.directory import Directory
from assignment_submission_checker.git_utils import switch_if_safe

JsonData: TypeAlias = Dict[str, Any]


@pytest.fixture(scope="session")
def DATA_DIR() -> Path:
    return (Path(os.path.abspath(os.path.dirname(__file__))) / "data").resolve()


@pytest.fixture
def test_data_json(DATA_DIR) -> Path:
    return DATA_DIR / "template.json"


@pytest.fixture
def test_data_dict(test_data_json: Path) -> JsonData:
    with open(test_data_json, "r") as f:
        data = json.load(f)
    return data


## DIRECTORIES


@pytest.fixture
def test_dir_structure(test_data_dict: JsonData) -> Directory:
    return Directory("root", test_data_dict["structure"], parent=None)


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


@pytest.fixture
def setup_submission_folder(
    setup_folder_structure,
    tmp_path: Path,
    git_repo_loc: Optional[str],
    git_commit_work_to: Optional[str],
    git_switch_to: Optional[str],
):
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

    # Run test
    yield


## ASSIGNMENTS


@pytest.fixture
def test_data_assignment(test_data_json: Path) -> Assignment:
    return Assignment.from_json(test_data_json)
