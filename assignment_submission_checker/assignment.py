from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .directory import Directory, DirectoryDict
from .utils import copy_tree

DIR_STRUCTURE_KEY = "structure"
GIT_BRANCH_KEY = "git-marking-branch"
ID_KEY = "number"
OTHER_BRANCHES_KEY = "git-alternative-branches"
TITLE_KEY = "title"
YEAR_KEY = "year"

OPTIONAL_KEYS = [
    DIR_STRUCTURE_KEY,
    GIT_BRANCH_KEY,
    ID_KEY,
    OTHER_BRANCHES_KEY,
    TITLE_KEY,
    YEAR_KEY,
]


class Assignment:

    _git_allowable_branches: List[str]
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
    def git_allowable_branches(self) -> List[str]:
        if self._git_allowable_branches is not None:
            return self._git_allowable_branches
        else:
            return []

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
    def from_json(cls, file: Optional[Path] = None, json_str: Optional[str] = None) -> Assignment:
        """
        Creates an `Assignment` instance by reading a json file, or a json-encoded string.

        Reading from a file trumps reading a string.

        :param file: Path to a compatible json file.
        :param json_str: String encoding a valid json file, which can be loaded with `json.loads`.
        :returns: An `Assignment` instance with the specification found in the file.
        """
        if file is not None:
            with open(file, "r") as f:
                json_info = json.load(f)
        elif json_str is not None:
            json_info = json.loads(json_str)
        else:
            raise RuntimeError("Please provide either a valid file path, or json string.")

        for key in OPTIONAL_KEYS:
            if key not in json_info:
                json_info[key] = None
        return Assignment(
            git_branch_to_mark=json_info[GIT_BRANCH_KEY],
            git_other_branches=json_info[OTHER_BRANCHES_KEY],
            id=json_info[ID_KEY],
            structure=json_info[DIR_STRUCTURE_KEY],
            title=json_info[TITLE_KEY],
            year=json_info[YEAR_KEY],
        )

    def __init__(
        self,
        git_branch_to_mark: Optional[str] = None,
        git_other_branches: Optional[List[str]] = None,
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
        self._git_allowable_branches = git_other_branches
        self.directory_structure = Directory("root", structure)
        self.id = str(id).rjust(3, "0")
        self.title = str(title)
        self.year = int(year)

    def validate_assignment(
        self, submission_dir: Path, tmp_dir: Path, ignore_extra_files: Optional[List[str]] = None
    ) -> str:
        """
        Validates that the submission directory provided matches the specifications of this instance.

        The validation process creates a copy of the submission directory and the directory tree
        beneath it, so operations like git checkouts can be conducted without altering the user's
        working directory.

        The temporary directory is always manually cleaned up by the program, though the
        OS should handle this if an uncaught error is encountered.

        :param submission_dir: Path to the root submission directory.
        :param tmp_dir: Temporary directory to use to unpack and validate submission.
        :param ignore_extra_files: Suppress warnings about unexpected files that match the patterns given.
        """
        # Copy to the temporary directory
        submission = copy_tree(submission_dir, tmp_dir, into=True)

        # Check the submission content
        check_log = self.directory_structure.check_against_directory(
            submission,
            do_not_set_name=False,
            *self.git_allowable_branches,
        )

        # Filter warnings gathered for any file patterns that we have been told to ignore
        if ignore_extra_files:
            check_log.ignore_unexpected_files(ignore_extra_files, relative_to=submission)

        return check_log.parse()
