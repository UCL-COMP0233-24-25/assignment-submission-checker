from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .directory import Directory, DirectoryDict
from .utils import AssignmentCheckerError, copy_tree

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

    def parse_into_output(
        self,
        fatal: AssignmentCheckerError | None,
        warnings: List[str] = [],
        information: List[str] = [],
    ) -> str:
        """
        Parses the output from assignment validation into a human-readable string that reports
        the findings of the validation process.
        """
        # Report should start with a header so it is clear which assignment spec the user
        # is validating against.
        main_heading = "Validation Report"
        heading_str = f"{main_heading}\n{'-' * len(main_heading)}"

        # If fatal is not None, it will be an AssignmentCheckerError which has prevented
        # the validation from completing. It also implies the submission is in the wrong
        # format. This should be clearly highlighted.
        fatal_heading = "ERROR IN SUBMISSION FORMAT DETECTED"
        fatal_str = ""
        if fatal is not None:
            fatal_str = (
                f"{fatal_heading}\n"
                f"{'-' * len(fatal_heading)}\n"
                "The assignment checker encountered the following error in your submission format. "
                "This has prevented complete validation of your assignment format.\n"
                "\t" + str(fatal).replace("\n", "\n\t")
            )

        # Warnings and Information should be lists, obtained in sequence from recursing down
        # the directory tree.
        # As such, it should be possible to just combine these line-by-line.
        warnings_heading = "Warnings"
        warnings_str = ""
        if warnings:
            warnings_str = (
                f"{warnings_heading}\n"
                f"{'-' * len(warnings_heading)}\n"
                "Encountered the following problems with your submission:\n\t"
            ) + "\n".join(s.replace("\n", "\n\t") for s in warnings)

        information_heading = "Information"
        information_str = ""
        if information:
            information_str = (
                f"{information_heading}\n"
                f"{'-' * len(information_heading)}\n"
                "Additional information gathered during the validation. "
                "Information reported here does not invalidate the submission, "
                "though you may wish to check you expect everything here to apply "
                "to your submission.\n\t"
            ) + "\n\t".join(s.replace("\n", "\n\t") for s in information)

        if (not fatal_str) and (not warnings_str) and (not information_str):
            return f"{heading_str}\nSubmission format matches specifications, nothing further to report."
        return (
            "\n\n".join([s for s in [heading_str, fatal_str, warnings_str, information_str] if s])
            + "\n"
        )

    def validate_assignment(self, submission_dir: Path, tmp_dir: Path) -> str:
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
        # Copy to the temporary directory
        submission = copy_tree(submission_dir, tmp_dir, into=True)

        # Check the submission content
        fatal, warnings, information = self.directory_structure.check_against_directory(
            submission, do_not_set_name=False, *self.git_allowable_branches
        )

        # Parse the output into a string,
        # and return
        return self.parse_into_output(fatal, warnings, information)
