import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Optional

import requests
from git import Repo

from assignment_submission_checker.assignment import Assignment
from assignment_submission_checker.utils import provide_tmp_directory

ASSIGNMENT_SPEC_REFERENCES = (
    "https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/tree/main/specs"
)
GH_RAW_FETCH = "https://raw.githubusercontent.com/UCL-COMP0233-24-25/assignment-submission-checker/refs/heads/main/specs"


def fetch_spec(assignment_spec: str) -> None:
    """
    Fetches the assignment specification given from the assignment checker repository.

    Raises a runtime error if the assignment specification is not recognised.
    """
    send_to = f"{GH_RAW_FETCH}/{assignment_spec}.json"
    r = requests.get(send_to)
    if not r.ok:
        raise RuntimeError(
            f"Failed to locate assignment specification {assignment_spec}, "
            "please check the reference you have provided. "
            f"You can view all available references at {ASSIGNMENT_SPEC_REFERENCES}"
        )
    return r.text


def infer_repo_name(repo: Repo) -> str:
    """
    Attempt to infer the name of a repository cloned from GitHub.
    """
    return repo.remotes.origin.url.split(".git")[0].split("/")[-1]


def main(
    assignment_lookup: Optional[str] = None,
    github_clone_url: Optional[str] = None,
    local_specs: Optional[Path] = None,
    submission: Optional[Path] = None,
) -> None:
    """
    Online specs take priority over local specs (assignment > local_specs)
    Online repo takes priority over local submission (github_clone_url > submission)
    """
    if assignment_lookup is not None:
        assignment = Assignment.from_json(json_str=fetch_spec(assignment_lookup))
    elif local_specs is not None:
        assignment = Assignment.from_json(Path(local_specs))
    else:
        raise RuntimeError("Need at least one of assignment or local_specs arguments.")

    if github_clone_url is not None:
        # Attempt to clone GH repo and place into temp folder
        # then set that as the submission directory
        tmp_dir = Path(mkdtemp("safe_clone"))
        clone_dir = tmp_dir / "cloned"
        clone_dir.mkdir(exist_ok=True)

        # Actually clone the repo from GH so it is available on the filesystem
        r = Repo.clone_from(github_clone_url, to_path=clone_dir)
        # Make sure we capture all branches from the remote
        default_branch = r.head
        for ref in r.remote().refs:
            r.git.checkout(ref.name.split("/")[-1])
        # Leave on the default branch
        r.git.checkout(default_branch)
        repo_name = infer_repo_name(r)
        r.close()

        # Relocate the cloned repository deeper inside another temporary folder, so that
        # names match up with those expected.
        submission_dir = tmp_dir / repo_name
        shutil.move(clone_dir, submission_dir)

    elif submission is not None:
        submission_dir = Path(submission)
    else:
        raise RuntimeError("Need either a local submission folder or a GH repo to clone.")

    # Setup validator with a temporary directory.
    # Note that this does mean we may have two copies of the repository on the file system,
    # but this is safer than risking a clone directly into /tmp.
    @provide_tmp_directory(
        clean_on_error=True,
        clean_on_success=True,
        pass_dir_as_arg="tmp_dir",
    )
    def validator(tmp_dir: Path) -> str:
        return assignment.validate_assignment(
            submission_dir=submission_dir,
            tmp_dir=tmp_dir,
        )

    # Validate and collect output
    return validator()
