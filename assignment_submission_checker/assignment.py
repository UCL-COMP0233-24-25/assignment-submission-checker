from __future__ import annotations

from datetime import datetime
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional

from .directory import Directory, DirectoryDict
from .utils import AssignmentCheckerError, on_readonly_error

DIR_STRUCTURE_KEY = "structure"
GIT_BRANCH_KEY = "git-marking-branch"
ID_KEY = "number"
TITLE_KEY = "title"
YEAR_KEY = "year"

OPTIONAL_KEYS = [
    DIR_STRUCTURE_KEY,
    GIT_BRANCH_KEY,
    ID_KEY,
    TITLE_KEY,
    YEAR_KEY,
]


class Assignment:

    _git_branch_to_mark: str
    directory_structure: Directory
    id: str
    title: str
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

    @property
    def name(self) -> str:
        """Assignment {number}, {academic year}: {title}"""
        return f"Assignment {self.id}, {self.academic_year}: {self.title}"

    @classmethod
    def from_json(cls, file: Path) -> Assignment:
        """
        Creates an `Assignment` instance by reading in a json file containing specifications.

        :param file: Path to a compatible json file.
        :returns: An `Assignment` instance with the specification found in the file.
        """
        with open(file, "r") as f:
            json_info = json.load(f)

        for key in OPTIONAL_KEYS:
            if key not in json_info:
                json_info[key] = None
        return Assignment(
            git_branch_to_mark=json_info[GIT_BRANCH_KEY],
            id=json_info[ID_KEY],
            structure=json_info[DIR_STRUCTURE_KEY],
            title=json_info[TITLE_KEY],
            year=json_info[YEAR_KEY],
        )

    def __init__(
        self,
        git_branch_to_mark: Optional[str] = None,
        id: Optional[int | str] = None,
        structure: Optional[DirectoryDict] = None,
        title: Optional[str] = None,
        year: Optional[int | str] = None,
    ) -> None:
        if id is None:
            id = 1
        if structure is None:
            structure = {}
        if not title:
            title = "<No title given>"
        if year is None:
            year = datetime.now().year

        self._git_branch_to_mark = git_branch_to_mark
        self.directory_structure = Directory("root", structure)
        self.id = str(id).rjust(2, "0")
        self.title = str(title)
        self.year = int(year)

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
        Validates that the submission directory provided matches the specifications of this instance.

        The validation process creates a copy of the submission directory and the directory tree
        beneath it, so operations like git checkouts can be conducted without altering the user's
        working directory.

        The temporary directory is always manually cleaned up by the program, though the
        OS should handle this if an uncaught error is encountered.

        :param submission_dir: Path to the root submission directory.
        :returns: FIXME
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
