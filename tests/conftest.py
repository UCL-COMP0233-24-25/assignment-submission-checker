import json
import os
from pathlib import Path
from typing import Any, Dict, Generator, List

import git
import pytest

# from assignment_submission_checker.assignment import Assignment
from assignment_submission_checker.directory import Directory
from assignment_submission_checker.git_utils import locate_repo_in_tree, switch_if_safe


def make_nested_dirs(where: Path, dir_dict: Dict[str, List[str | Dict]]) -> None:
    """
    Creates the given folder structure at the path provided.

    The dir_dict argument should be a dictionary that describes the file structure to create.
    The keys should be strings, corresponding to directory names to create.
    Values should be a list of either strings, or further dictionaries of the same format.
    - Strings in the list will be interpreted as file names to be created.
    - Dictionaries in the list will be interpreted as subdirectories to create.
    - Providing an empty list as the value will create an empty directory.
    """
    for dir_name, dir_objs in dir_dict.items():
        new_dir = where / dir_name
        new_dir.mkdir(parents=False, exist_ok=True)

        # Populate with files
        for f_name in [name for name in dir_objs if isinstance(name, str)]:
            with open(new_dir / f_name, "w") as f:
                f.write("Placeholder content")

        # Create subdirectories
        for subdir in [subdir for subdir in dir_objs if isinstance(subdir, dict)]:
            make_nested_dirs(new_dir, subdir)
    return


@pytest.fixture(scope="session")
def DATA_DIR() -> Path:
    return (Path(os.path.abspath(os.path.dirname(__file__))) / "data").resolve()


@pytest.fixture
def make_folder_structure(tmp_path: Path, request) -> Generator[None, Any, None]:
    """
    Creates the given folder structure in the temporary path.

    request.param should be either:
    - A dictionary compatible with the make_folder_structure function's dir_dict argument.
    - A string that matches the name of a pytest fixture that returns a dictionary compatible
    with the make_folder_structure function's dir_dict argument.
    """
    if isinstance(request.param, str):
        dir_dict = request.getfixturevalue(request.param)
    elif isinstance(request.param, dict):
        dir_dict = request.param
    else:
        raise RuntimeError(
            "Need a dictionary argument or a fixture name that generates a dictionary."
        )
    make_nested_dirs(where=tmp_path, dir_dict=dir_dict)
    yield


## template.json fixtures and derived objects


@pytest.fixture
def template_json(DATA_DIR) -> Path:
    return DATA_DIR / "template.json"


@pytest.fixture
def template_loaded_json(template_json: Path) -> Dict[str, Any]:
    with open(template_json, "r") as f:
        data = json.load(f)
    return data


@pytest.fixture
def template_dir_dict() -> Dict[str, List[str | Dict]]:
    """
    A file structure that matches that in template.json.
    """
    return {
        "top-level-folder": [
            {
                "my-git-submission": [
                    "c1.py",
                    "c2.py",
                    {
                        "report": [
                            "report.md",
                            "plot.png",
                            "AIUsage.md",
                        ],
                        "data": [
                            "custom_data.csv",
                        ],
                    },
                ]
            },
        ],
    }


@pytest.fixture
def bad_template_dir_dict() -> Dict[str, List[str | Dict]]:
    """
    A file structure that matches that in template.json, but:

    - Is missing the compulsory my-git-submission/c2.py file,
    - report/extra_image.png is an unexpected file,
    - data/wrong_format.json is an unexpected file.
    """
    return {
        "top-level-folder": [
            {
                "my-git-submission": [
                    "c1.py",
                    {
                        "report": [
                            "report.md",
                            "plot.png",
                            "extra_image.png",
                        ],
                        "data": [
                            "good_format.csv",
                            "wrong_format.json",
                        ],
                    },
                ]
            }
        ]
    }


@pytest.fixture
def template_directory(template_loaded_json: Dict[str, Any]) -> Directory:
    """
    Directory instance corresponding to the structure key in template.json.

    Top-level folder has a variable name, which takes the name 'structure' until set.
    """
    return Directory("structure", template_loaded_json["structure"], parent=None)


## DIRECTORIES


@pytest.fixture
def setup_folder_structure_with_git(
    make_folder_structure,
    tmp_path: Path,
    request,
) -> Generator[None, Any, None]:
    """
    Sets up the folder structure provided, potentially adding a git repository to the file structure.

    request.param should be a dictionary that contains the following keys,
    or the name of a fixture that returns such a dictionary;

    - 'checkout': The value of this key should be a string giving the name of the branch to checkout after
    committing the files, leaving the repository on. Defaults to 'main' if not provided.
    - 'commit': The value of this key should be a string giving the name of the branch to commit files
    created in `make_folder_structure` to. Defaults to 'main' if not provided.
    - 'rootdir': The value of this key should be a string or Path-like object that specifies the folder to
    initialise the git repository in.
    It will default to the top-level directory in `make_folder_structure` if not provided.
    """
    params = request.param
    if isinstance(params, str):
        params = request.getfixturevalue(params)
    if isinstance(params, dict):
        leave_repo_on_branch = params["checkout"] if "checkout" in params else None
        commit_work_to_branch = params["commit"] if "commit" in params else "main"
        make_git_root_at = params["rootdir"] if "rootdir" in params else "."
    else:
        commit_work_to_branch = "main"
        leave_repo_on_branch = None
        make_git_root_at = "."

    repo_dir = tmp_path / make_git_root_at
    if not repo_dir.is_dir():
        raise RuntimeError("Target git folder needs to exist!")

    repo = git.Repo.init(repo_dir)
    # Ensure that the branch we made with git init has the same name as
    # the branch we want to commit to.
    # This avoids issues if the system git initialises repositories with
    # a default branch that takes the name 'main', or similar, that we don't
    # want to include in the repository for testing reasons.
    if repo.active_branch.name != commit_work_to_branch:
        repo.git.branch("-m", commit_work_to_branch)
    repo.git.commit("--allow-empty", "-m", "Initial commit to main")

    # Commit all work to this branch
    repo.git.add(".")
    repo.git.commit("-m", "Commit all work.")

    # Switch to the branch that we want the repo left on,
    # otherwise stay on the branch we committed work to.
    if leave_repo_on_branch is not None:
        switch_if_safe(repo, leave_repo_on_branch, create=True)

    # Run test
    yield


@pytest.fixture
def setup_submission(
    setup_folder_structure_with_git,
    tmp_path: Path,
    request,
) -> Generator[None, Any, None]:
    """
    Sets up a submission folder structure, including a git repository, and allowing for the possibility that
    the working tree of the git repository is dirty.

    request.param should be a dictionary with the following keys:
    - "uncommitted": Files tracked by the repository that should be edited, added, but not committed.
    - "unstaged": Files tracked by the repository that should be edited and not staged.
    - "untracked": Files to create but not add to the repository.

    Values of these keys should be lists of Path (or str) instances that provide the path - relative to the repository
    root - to the file to be created / edited.
    Note that other 'polluting' files that are not affected by the git repository can be added
    when calling `make_folder_structure`.
    """
    params = request.param
    if isinstance(params, dict):
        uncommitted = params["uncommitted"] if "uncommitted" in params else []
        unstaged = params["unstaged"] if "unstaged" in params else []
        untracked = params["untracked"] if "untracked" in params else []
    else:
        uncommitted = []
        unstaged = []
        untracked = []

    repo_loc = locate_repo_in_tree(tmp_path)
    if repo_loc is None:
        raise RuntimeError(
            f"Could not find git repository somewhere in the tree starting at {tmp_path}."
        )
    repo = git.Repo(repo_loc)

    # Files that are not tracked by the repository
    for file in [Path(f) for f in untracked]:
        with open(repo_loc / file, "w") as f:
            f.write("Untracked file.")

    # Edit files tracked by the repository, and don't stage the changes
    for file in [Path(f) for f in unstaged]:
        to_edit = repo_loc / file
        assert to_edit.is_file(), f"File {to_edit} is not a file!"
        with open(to_edit, "w") as f:
            f.write("Overwrite lines in this file, leaving out of the staging area.")

    # Edit files tracked by the repository, add to staging area,
    # but don't commit the changes
    for file in [Path(f) for f in uncommitted]:
        to_edit = repo_loc / file
        assert to_edit.is_file(), f"File {to_edit} is not a file!"
        with open(to_edit, "w") as f:
            f.write("Overwrite lines in this file, leaving uncommitted.")
        repo.git.add(to_edit)

    repo.close()
    yield
