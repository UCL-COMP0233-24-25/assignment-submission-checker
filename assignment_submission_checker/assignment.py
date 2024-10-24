from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional
from warnings import warn

from .directory import Directory, DirectoryDict
from .utils import AssignmentCheckerError, on_readonly_error

ARCHIVE_PATH_KEY = "archive-path"
DIR_STRUCTURE_KEY = "structure"
GIT_BRANCH_KEY = "git-marking-branch"
ID_KEY = "number"
YEAR_KEY = "year"


class Assignment:

    _git_branch_to_mark: str
    assignment_id: str
    directory_structure: Directory
    git_repo_path: Path
    year: int

    @property
    def academic_year(self) -> str:
        """Academic year that the assignment was/is released in."""
        return f"{self.year}-{self.year+1}"

    @property
    def git_branch_to_mark(self) -> str:
        if self._git_branch_to_mark is not None:
            return self._git_branch_to_mark
        else:
            return "main"

    @classmethod
    def copy_to_tmp_location(cls, target_directory: Path, tmp_dir: Path) -> None:
        """
        Should return the path to the copied directory!
        """
        if isinstance(target_directory, str):
            target_directory = Path(target_directory)

        if not target_directory.is_dir():
            raise AssignmentCheckerError(f"Target {target_directory} is not a directory.")

        try:
            shutil.copytree(target_directory, tmp_dir, symlinks=False, dirs_exist_ok=False)
        except Exception as e:
            raise AssignmentCheckerError(
                f"Could not copy the submission directory {target_directory} to a temporary location, encountered the following error:\n\t{str(e)}."
            )

    @classmethod
    def from_json(cls, file: Path) -> Assignment:
        with open(file, "r") as f:
            json_info = json.load(f)

        return Assignment(
            git_branch_to_mark=json_info[GIT_BRANCH_KEY] if GIT_BRANCH_KEY in json_info else None,
            number=json_info[ID_KEY],
            year=json_info[YEAR_KEY],
            structure=json_info[DIR_STRUCTURE_KEY],
        )

    def __init__(
        self,
        git_branch_to_mark: Optional[str] = None,
        number: int | str = 1,
        structure: DirectoryDict = {},
        year: int = 2024,
    ) -> None:
        self._git_branch_to_mark = git_branch_to_mark

        self.assignment_id = number if isinstance(number, str) else str(number).zfill(2)
        self.directory_structure = Directory("root", structure)
        self.year = year

        # Locate any directories that should be git repositories.
        # Throw an error if there is not exactly 1.
        git_repos = [d for d in self.directory_structure if d.git_root]
        if len(git_repos) != 1:
            raise RuntimeError(
                f"Assignment has {len(git_repos)} directories defined as git repositories."
            )
        self.git_repo = git_repos[0].path_from_root

    def _inner_check_submission(self, submission_dir: Path, tmp_dir: Path) -> None:
        """
        Wrapped steps for the check_submission method.

        We do not have to worry about cleaning up the temporary directory, since the
        outer wrapping method will take care of this.
        We should also be able to edit the temporary directory's contents as we see fit.
        """
        # REWORK ME!
        # self.copy_to_tmp_location(target_directory=submission_dir, tmp_dir=tmp_dir)

        # # Assert that a single folder has now been placed into the temporary directory
        # path_objs = os.listdir(tmp_dir)
        # file_objs = [f for f in path_objs if os.path.isfile(f)]
        # dir_objs = [Path(f) for f in path_objs if os.path.isdir(f)]

        # if file_objs:
        #     warn(
        #         "The following files were present at top-level after extracting your submission:\n"
        #         "".join(f"\t{f}\n" for f in file_objs)
        #     )

        # submission_dir = None
        # if not dir_objs:
        #     raise AssignmentCheckerError("FATAL: No directory produced when extracting archive.")
        # else:
        #     if len(dir_objs) == 1:
        #         submission_dir = tmp_dir / dir_objs[0]
        #     else:
        #         warn(
        #             f"Detected multiple top-level directories when extracting your archive: {dir_objs}"
        #         )
        #         # Check if the extra directories are hidden, which could indicate metadata files from OSes
        #         hidden_dirs = [d for d in dir_objs if str(d).startswith(".")]
        #         non_hidden_dirs = list(set(dir_objs) - set(hidden_dirs))
        #         if len(non_hidden_dirs) == 1:
        #             submission_dir = tmp_dir / non_hidden_dirs[0]
        #         else:
        #             raise AssignmentCheckerError(
        #                 "You have multiple top-level directories within your submission folder."
        #             )

        # # Start the checking process
        # if submission_dir is not None:
        #     self.directory_structure.check_against_directory(submission_dir)
        # else:
        #     raise

    def check_submission(self, submission_dir: Path) -> AssignmentCheckerError | Any:
        """
        Check the archive provided matches the assignment specifications that have been read in.
        """
        unpacking_directory = tempfile.mkdtemp()
        raised_error = None

        try:
            output_from_wrapped_fn = self._inner_check_submission(
                submission_dir=submission_dir,
                tmp_dir=unpacking_directory,
            )
            shutil.rmtree(unpacking_directory, onerror=on_readonly_error)
        except Exception as e:
            raised_error = e
            shutil.rmtree(unpacking_directory, onerror=on_readonly_error)

        return raised_error if raised_error is not None else output_from_wrapped_fn
