from pathlib import Path
from typing import List, Tuple
from warnings import warn

import git

from .utils import AssignmentCheckerError


def is_clean(repo: git.Repo, boolean_output: bool = False) -> Tuple[List[str], List[str]] | bool:
    """
    Determine if the repository has a clean working tree.

    Returns a Tuple of two values;
        1. A list of the untracked files in the repository.
        2. A list of the changed files in the repository.

    In the event that boolean_output is True, instead just returns True/False if the repository
    is clean/unclean.
    """
    untracked_files = []
    changed_files = []

    repo_clean = not repo.is_dirty(untracked_files=True)

    if not repo_clean:
        untracked_files = repo.untracked_files
        changed_files = [item.a_path for item in repo.index.diff(None)]

    return untracked_files, changed_files if not boolean_output else repo_clean


def is_git_repo(git_root_dir: Path) -> bool:
    """
    Returns True if a valid git repository is found at the directory provided,
    and False otherwise.
    """
    try:
        repo = git.Repo(git_root_dir)
        repo.close()
    except Exception:
        return False
    return True


def switch_to_main_if_possible(repo: git.Repo, *allowable_other_names: str) -> None:
    """
    Switches the main branch in the repo, if this is possible.

    If the main branch doesn't exist, the method will attempt to switch to the
    allowable other names, in the order they are provided. It will switch to the first
    name that it finds a reference to.

    Raises an AssignmentCheckerError if the branch cannot be switched to.
    """
    correct_ref = None
    if repo.active_branch.name == "main":
        return
    elif "main" in [r.name for r in repo.references]:
        warn("Repository was not on the main branch, switching now...")
        correct_ref = "main"
    else:
        # Attempt to switch to any of the other available references.
        for ref in allowable_other_names:
            if ref.name in repo.references:
                warn(
                    f"Repository does not have a main branch, but found {ref.name}, which is an acceptable alternative. Switching now..."
                )
                correct_ref = ref.name

    try:
        repo.git.checkout(correct_ref)
    except Exception as e:
        raise AssignmentCheckerError(
            f"Could not checkout reference {correct_ref} in repository."
        ) from e
    return