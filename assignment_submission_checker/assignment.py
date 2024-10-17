from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
import zipfile
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

    _archive_format: str = ".tar.gz"

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
    def expected_archive_format(self) -> str:
        """
        The format of the submission archive that this assignment expects to receive.

        If the format of the submission archive cannot be inferred from the name of the archive itself,
        then the assignment will treat it as this format.
        """
        return self._archive_format

    @expected_archive_format.setter
    def expected_archive_format(self, fmt: str) -> None:
        if fmt not in [".tar.gz", ".zip"]:
            raise ValueError(f"Extraction of {fmt} archives is not supported by this tool.")
        self._archive_format = fmt

    @property
    def git_branch_to_mark(self) -> str:
        if self._git_branch_to_mark is not None:
            return self._git_branch_to_mark
        else:
            return "main"

    @classmethod
    def extract_to(cls, target_archive: Path, tmp_dir: Path) -> None:
        if isinstance(target_archive, str):
            target_archive = Path(target_archive)

        if target_archive.suffixes:
            archive_extension = "".join(target_archive.suffixes)
        else:
            warn(
                f"Could not infer archive format from path: {target_archive}. Treating as {cls.expected_archive_format}."
            )
            archive_extension = cls.expected_archive_format

        try:
            if archive_extension == ".tar.gz":
                tarfile.open(target_archive).extractall(path=tmp_dir)
            elif archive_extension == ".zip":
                zipfile.ZipFile(target_archive).extractall(path=tmp_dir)
        except Exception as e:
            raise AssignmentCheckerError(
                f"Could not extract the file {target_archive} as a {archive_extension} file, encountered the following error:\n\t{str(e)}.\nMake sure you have compressed your assignment using the correct compression tool (tar/zip) and have provided the correct path to your submission file."
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
        archive_format: str = ".tar.gz",
        git_branch_to_mark: Optional[str] = None,
        number: int | str = 1,
        structure: DirectoryDict = {},
        year: int = 2024,
    ) -> None:
        self._git_branch_to_mark = git_branch_to_mark

        self.expected_archive_format = archive_format
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

    def _inner_check_submission(self, target_archive: Path, tmp_dir: Path) -> None:
        """
        Wrapped steps for the check_submission method.

        We do not have to worry about cleaning up the temporary directory, since the
        outer wrapping method will take care of this.
        We should also be able to edit the temporary directory's contents as we see fit.
        """
        # First, extract the target_archive to the temporary directory.
        self.extract_to(target_archive=target_archive, tmp_dir=tmp_dir)

        # Assert that a single folder has now been placed into the temporary directory
        path_objs = os.listdir(tmp_dir)
        file_objs = [f for f in path_objs if os.path.isfile(f)]
        dir_objs = [Path(f) for f in path_objs if os.path.isdir(f)]

        if file_objs:
            warn(
                "The following files were present at top-level after extracting your submission:\n"
                "".join(f"\t{f}\n" for f in file_objs)
            )

        submission_dir = None
        if not dir_objs:
            raise AssignmentCheckerError("FATAL: No directory produced when extracting archive.")
        else:
            if len(dir_objs) == 1:
                submission_dir = tmp_dir / dir_objs[0]
            else:
                warn(
                    f"Detected multiple top-level directories when extracting your archive: {dir_objs}"
                )
                # Check if the extra directories are hidden, which could indicate metadata files from OSes
                hidden_dirs = [d for d in dir_objs if str(d).startswith(".")]
                non_hidden_dirs = list(set(dir_objs) - set(hidden_dirs))
                if len(non_hidden_dirs) == 1:
                    submission_dir = tmp_dir / non_hidden_dirs[0]
                else:
                    raise AssignmentCheckerError(
                        "You have multiple top-level directories within your submission folder."
                    )

        # Start the checking process
        if submission_dir is not None:
            self.directory_structure.check_against_directory(submission_dir)
        else:
            raise

    def check_submission(self, target_archive: Path) -> AssignmentCheckerError | Any:
        """
        Check the archive provided matches the assignment specifications that have been read in.
        """
        unpacking_directory = tempfile.mkdtemp()
        raised_error = None

        try:
            output_from_wrapped_fn = self.check_submission(
                target_archive=target_archive,
                tmp_dir=unpacking_directory,
            )
            shutil.rmtree(unpacking_directory, onerror=on_readonly_error)
        except Exception as e:
            raised_error = e
            shutil.rmtree(unpacking_directory, onerror=on_readonly_error)

        return raised_error if raised_error is not None else output_from_wrapped_fn
