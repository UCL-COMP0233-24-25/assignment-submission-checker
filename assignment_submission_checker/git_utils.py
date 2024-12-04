import os
from pathlib import Path
from typing import List, Tuple

import git

from assignment_submission_checker.logging.log_entry import LogEntry
from assignment_submission_checker.logging.log_types import LogType

GIT_ROOT_PATTERNS = [
    "README*",
    "LICENSE*",
    "*.ini",
    "*.in",
    "*.yaml",
    ".gitignore",
]


def clone_and_fetch_all_refs(clone_url: str, clone_into: Path) -> str:
    """
    Clone a remote repository from the `clone_url` provided, into the `clone_into` location.

    Method returns the name of the remote repository that was fetched, if it can be inferred.
    """
    r = git.Repo.clone_from(clone_url, to_path=clone_into)

    # Make sure we capture all branches from the remote
    default_branch = r.head
    for ref in r.remote().refs:
        r.git.checkout(ref.name.split("/")[-1])

    # Leave on the default branch
    r.git.checkout(default_branch)
    repo_name = infer_repo_name(r)
    r.close()

    return repo_name


def infer_repo_name(repo: git.Repo) -> str:
    """
    Attempt to infer the name of a repository cloned from GitHub.
    """
    return repo.remotes.origin.url.split(".git")[0].split("/")[-1]


def is_clean(
    repo: git.Repo, boolean_output: bool = False
) -> Tuple[List[str], List[str], List[str]] | bool:
    """
    Determine if the repository has a clean working tree.

    Returns a Tuple of two values;
        1. A list of the untracked files in the repository.
        2. A list of the changed files in the repository.

    In the event that boolean_output is True, instead just returns True/False if the repository
    is clean/unclean.
    """
    untracked_files = []
    unstaged_files = []
    uncommitted_files = []

    repo_clean = not repo.is_dirty(untracked_files=True)

    if not repo_clean:
        untracked_files = repo.untracked_files
        unstaged_files = [item.a_path for item in repo.index.diff(None)]
        uncommitted_files = [item.a_path for item in repo.index.diff("HEAD")]

    return untracked_files, unstaged_files, uncommitted_files if not boolean_output else repo_clean


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


def locate_repo_in_tree(search_root: Path) -> Path:
    """
    Given a root folder to search from, recurse through the directory tree from this location and return the path to
    the first git repository that is found.

    If no repository is found, the return value is None.
    """
    search_root = Path(search_root)

    try:
        r = git.Repo(search_root)
    except git.InvalidGitRepositoryError:
        r = None

    if r is not None:
        r.close()
        return search_root
    else:
        # This directory is not a valid git repository,
        # start recursing.
        for dir in [search_root / p for p in os.listdir(search_root)]:
            if dir.is_dir():
                answer = locate_repo_in_tree(dir)
            if answer is not None:
                return answer


def switch_if_safe(repo: git.Repo, to_branch: str, create: bool = False) -> None:
    """
    Switch to the given reference using git switch.

    If the reference doesn't exist, passing the "create" flag will create the branch and switch to it.
    Otherwise, an error will be raised via reporting the invalid reference.
    """
    if repo.active_branch.name == to_branch:
        return
    elif to_branch in [ref.name for ref in repo.references]:
        repo.git.switch(to_branch)
    elif create:
        repo.git.switch("-c", to_branch)
    else:
        raise RuntimeError(f"Reference {to_branch} not in repository references.")


def switch_to_main_if_possible(repo: git.Repo, *allowable_other_names: str) -> LogEntry:
    """
    Switches the main branch in the repo, if this is possible.

    If the main branch doesn't exist, the method will attempt to switch to the
    allowable other names, in the order they are provided. It will switch to the first
    name that it finds a reference to.

    The returned value will be a string that describes any non-fatal warnings that were encountered when trying to
    switch the repository to the desired branch.
    Specifically:
    - If the repository was not already on the `main` branch.
    - If the repository has no `main` branch, but did have a branch corresponding to
    one of the `allowable_other_names`.

    Raises an AssignmentCheckerError if the branch cannot be switched to.
    """
    correct_ref = None
    warning_type = LogType.WARN

    if repo.active_branch.name == "main":
        return
    elif "main" in [r.name for r in repo.references]:
        warning_type = LogType.WARN_GIT_NOT_ON_MAIN
        correct_ref = "main"
    else:
        # Attempt to switch to any of the other available references.
        for name in allowable_other_names:
            if name in repo.references:
                warning_type = LogType.WARN_GIT_USES_MAIN_ALT
                correct_ref = name
                break

    if correct_ref is None:
        return LogEntry(LogType.FATAL_GIT_NO_VALID_BRANCH)
    try:
        repo.git.checkout(correct_ref)
    except Exception as e:
        return LogEntry(LogType.FATAL_GIT_CHECKOUT_FAILED, correct_ref, str(e))

    return LogEntry(warning_type, correct_ref)
