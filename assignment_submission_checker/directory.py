from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Optional, Set, Tuple, TypeAlias
from warnings import warn

import git

from .git_utils import is_clean, is_git_repo, switch_to_main_if_possible
from .utils import AssignmentCheckerError

DirectoryDict: TypeAlias = Dict[str, Any]

COMPULSORY_FILES_KEY = "compulsory"
DATA_PATTERNS_KEY = "data-file-types"
GIT_ROOT_KEY = "git-root"
OPTIONAL_FILES_KEY = "optional"
VARIABLE_NAME_KEY = "variable-name"

METADATA_KEYS = {
    COMPULSORY_FILES_KEY,
    DATA_PATTERNS_KEY,
    GIT_ROOT_KEY,
    OPTIONAL_FILES_KEY,
    VARIABLE_NAME_KEY,
}


class Directory:

    compulsory: List[str]
    data_file_patterns: List[str]
    git_root: bool = False
    name: str
    optional: List[str]
    parent: Directory
    subdirs: List[Directory]
    variable_name: bool

    @property
    def is_data_dir(self) -> bool:
        """
        Whether this directory is a 'data directory', that may contain data files with user-defined names.
        """
        return bool(self.data_file_patterns)

    @property
    def is_optional(self) -> bool:
        """
        Returns True if the directory is an optional inclusion in the submission,
        and returns False otherwise.

        A directory is optional if it contains no compulsory files.
        """
        return bool(self.compulsory)

    @property
    def path_from_root(self) -> Path:
        """
        Path to this directory, from the root of the directory tree.

        If self.parent = None, this Directory is assumed to be the root of the tree.
        """
        if self.parent is None:
            return Path(".")
        else:
            return self.parent.path_from_root / self.name

    def __init__(
        self, name: str, directory_structure: DirectoryDict = {}, parent: Optional[Directory] = None
    ) -> None:
        self.name = name
        self.parent = parent

        # Determine if this directory is the git root
        self.git_root = (
            directory_structure[GIT_ROOT_KEY] if GIT_ROOT_KEY in directory_structure else False
        )

        # Record compulsory and optional files
        self.compulsory = (
            sorted(directory_structure[COMPULSORY_FILES_KEY])
            if COMPULSORY_FILES_KEY in directory_structure
            else []
        )
        self.optional = (
            sorted(directory_structure[OPTIONAL_FILES_KEY])
            if OPTIONAL_FILES_KEY in directory_structure
            else []
        )

        # If this is a data directory, record the file patterns we expect to find in it.
        self.data_file_patterns = (
            sorted(directory_structure[DATA_PATTERNS_KEY])
            if DATA_PATTERNS_KEY in directory_structure
            else []
        )

        # Record if this directory may have a user-defined name
        self.variable_name = (
            directory_structure[VARIABLE_NAME_KEY]
            if VARIABLE_NAME_KEY in directory_structure
            else False
        )

        # Now, use recursion to create the list of directories that this directory contains.
        self.subdirs = sorted(
            Directory(name, info, parent=self)
            for name, info in directory_structure.items()
            if name not in METADATA_KEYS
        )

    def __getitem__(self, key: Path | str) -> Directory:
        """
        Fetch the subdirectory of this directory with the given name,
        if it exists.

        Passing a path-like string or Path will attempt to traverse the directory structure.
        """
        if isinstance(key, str):
            key = Path(key)
        if len(key.parts) == 0:
            return self
        elif key.parts[0] == "..":
            if self.parent:
                return self.parent
            else:
                raise ValueError(f"{self.name} is the root directory.")
        matched_directories = [d for d in self if d.path_from_root == key]
        if len(matched_directories) > 1:
            raise ValueError(f"{key} is the name of multiple subdirectories of {self.name}.")
        elif len(matched_directories) == 0:
            raise ValueError(f"{key} is not a subdirectory of {self.name}.")
        # There is assuredly 1 entry in the list now
        return matched_directories[0]

    def __iter__(self) -> Iterator[Directory]:
        return self.traverse()

    def __eq__(self, other: Directory) -> bool:
        """
        Directories are equal if they specify the same files,
        and contain the same subdirectories.
        """
        if not isinstance(other, Directory):
            return False
        # The two instances, at top level, are identical.
        truth_value = (
            (self.name == other.name or self.variable_name == other.variable_name)
            and self.git_root == other.git_root
            and set(self.compulsory) == set(other.compulsory)
            and set(self.data_file_patterns) == set(other.data_file_patterns)
            and set(self.optional) == set(other.optional)
        )
        # The subdirectories that each contains are equal.
        if len(self.subdirs) != len(other.subdirs):
            return False
        else:
            for my_subdir, their_subdir in zip(sorted(self.subdirs), sorted(other.subdirs)):
                truth_value = truth_value and (my_subdir == their_subdir)
        return truth_value

    def __le__(self, other: Directory) -> bool:
        return self.name <= other.name

    def __lt__(self, other: Directory) -> bool:
        return self.name < other.name

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        files = "\n".join(
            f"\t{file} [opt]" if file in self.optional else f"\t{file}"
            for file in sorted(self.compulsory + self.optional)
        )
        if files:
            files = f"\n{files}"

        optional_data_types = "\n".join(f"\t{pattern}" for pattern in self.data_file_patterns)
        if optional_data_types:
            optional_data_types = f"\n{optional_data_types}"

        subdirs = "\n".join(f"\t{directory}".replace("\n", "\n\t") for directory in self.subdirs)
        if subdirs:
            subdirs = f"\n{subdirs}"

        return f"{self.name}" + files + optional_data_types + subdirs

    def traverse(self) -> Generator[Directory]:
        """
        Traverse down the directory tree, yielding self first then descending into subdirectories.
        """
        yield self
        for d in self.subdirs:
            yield from d.traverse()

    def check_against_directory(self, directory: Path) -> bool:
        """
        Given a directory on the machine, determine if the contents of the directory are compatible with
        the expected setup of this Directory instance.

        This method will check (in order):

        - If the given directory exists on the machine.
        - Check the name of the given directory against self.name.
            - If self.variable_name, then infer the variable name (possibly throwing warnings to the user).
            - Otherwise, confirm that the directory name matches self.name.
        - Check if the directory is the git root.
            - If self.git_root is False, confirm the directory is not a git repository, then skip these steps.
            - Otherwise;
                - Determine if a git repo is present at the given directory.
                - Determine if the working tree is clean.
                - Attempt to switch to the marking branch (main).
        - Check the files are present in the directory.
            - Check that all compulsory files are present in the directory.
            - Check that there are no unexpected files in the directory.
        - Delegate the checking process to the subdirectories of this Directory instance.

        TODO: Subfolders with variable names need special treatment at the end (see comment).
        """
        if not directory.is_dir():
            raise RuntimeError(f"Is not a directory: {directory}")

        if self.variable_name:
            # Infer the name that the student has given to this directory.
            # This typically occurs when a student is asked to use their candidate number
            # for a directory, for example.
            if self.name == "root":
                print(
                    f"Inferred your candidate number as {directory.stem} - you will need to verify if this is correct."
                )
            else:
                warn(f"Matched {directory.stem} to folder {self.name} that has a variable name.")
            self.name = directory.stem
        elif self.name != directory.stem:
            raise RuntimeError(f"Directory {directory} does not have name {self.name}.")

        # If this is not meant to be a git repository, check as such.
        i_am_a_git_repo = is_git_repo(directory)
        if self.git_root:
            if not i_am_a_git_repo:
                raise AssignmentCheckerError(f"Git repository not found at {directory}.")

            repo = git.Repo(directory)

            # Check working tree
            untracked_files, changed_files = is_clean(repo)
            if untracked_files:
                raise AssignmentCheckerError(
                    f"You have untracked changes in your git repository: {untracked_files}"
                )
            elif changed_files:
                raise AssignmentCheckerError(
                    f"You have uncommitted changes in your git repository: {changed_files}"
                )

            # Switch to marking branch
            switch_to_main_if_possible(repo, "master")

            # Close repo to not interfere with other programs
            repo.close()
        elif i_am_a_git_repo:  # === (not self.git_repo and i_am_a_git_repo)
            raise AssignmentCheckerError(
                f"Git repository found at {directory}, which is not the expected location."
            )

        # Check the files and subdirectories that this folder contains.
        missing_compulsory, unexpected = self.check_files(directory)
        if missing_compulsory:
            raise AssignmentCheckerError(
                f"Your submission is missing the following compulsory files (not found in {directory}):\n"
                "".join(f"\t{f}\n" for f in missing_compulsory)
            )
        elif unexpected:
            warn(
                f"The following files were found in {directory}, but were not expected:\n"
                "".join(f"\t{f}\n" for f in unexpected)
            )

        # Delegate further investigation down into subdirectories.
        for subdir in [s for s in self.subdirs if not s.variable_name]:
            path_to_subdir = directory / subdir.name
            if not (subdir.is_optional or path_to_subdir.is_dir()):
                raise AssignmentCheckerError(
                    f"Expected subdirectory {subdir} to be present in {self.name}, but it is not."
                )
            subdir.check_against_directory(path_to_subdir)
        # If this folder contains subdirectories that have variable names,
        # we will need special treatment to try and match these to the remaining
        # directories we have not used in the above loop.
        # For now, this is left as an immediate error raise, since I don't have time to
        # implement it, and in practice this should never occur (only the root folder should have a variable name).
        for subdir in [s for s in self.subdirs if s.variable_name]:
            raise RuntimeError(
                "The assignment checker cannot handle subdirectories that have variable names. "
                "Only the submission root can have a variable name."
            )

    def check_files(self, directory: Path) -> Tuple[Set[str], Set[str]]:
        """
        Check the files that are present in the directory, returning:

        1. A list of compulsory files that are missing.
        2. A list of files that were not expected to be found.
        """
        files = set(f for f in os.listdir(directory) if os.path.isfile(directory / f))

        missing_compulsory = set(self.compulsory) - files

        data_files = set(
            file for pattern in self.data_file_patterns for file in fnmatch.filter(files, pattern)
        )
        unexpected = files - set(self.compulsory) - set(self.optional) - data_files

        return missing_compulsory, unexpected
