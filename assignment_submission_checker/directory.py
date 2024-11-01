from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Optional, Set, Tuple, TypeAlias

import git

from .git_utils import is_clean, is_git_repo, switch_to_main_if_possible
from .utils import AssignmentCheckerError, match_to_unique_assignments

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
    name_pattern: str
    optional: List[str]
    parent: Directory
    subdirs: List[Directory]

    @property
    def fixed_name_subdirs(self) -> List[Directory]:
        """
        Subdirectories of this Directory that do not have variable names.
        """
        return [s for s in self.subdirs if not s.variable_name]

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
        all_subdirs_are_optional = all(s.is_optional for s in self.subdirs)
        return all_subdirs_are_optional and not bool(self.compulsory)

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

    @property
    def variable_name(self) -> bool:
        """
        Whether this instance needs to match a name pattern.
        """
        return bool(self.name_pattern)

    @property
    def variable_name_subdirs(self) -> List[Directory]:
        """
        Subdirectories of this Directory that have variable names.
        """
        return [s for s in self.subdirs if s.variable_name]

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
        self.name_pattern = (
            directory_structure[VARIABLE_NAME_KEY]
            if VARIABLE_NAME_KEY in directory_structure
            else ""
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
            (self.name == other.name or self.name_pattern == other.name_pattern)
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

    def check_against_directory(
        self,
        directory: Path,
        do_not_set_name: bool = False,
        *substitutes_for_main_branch: str,
    ) -> Tuple[AssignmentCheckerError | None, List[str], List[str]]:
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

        During this process, the checking algorithm may encounter FATAL errors, or WARNINGS.

        FATAL errors make subsequent steps in the algorithm impossible:
            - When the directory does not exist on the filesystem.
            - When the name of the directory given does not match the fixed name of this instance.
            - When this directory should be a git repository, but is not.
            - When there are untracked changes within a git repository.
            - When there are uncommitted changes within a git repository.
            - When switching to `main` or another acceptable branch is impossible.
            - When a reference could not be checked out in the repository.
            - When a git repository is present in a directory that should not be a repository.
            - When a compulsory subdirectory is not present.
            - When a compulsory subdirectory with a variable name cannot be matched to a folder on the filesystem.

        WARNINGs report errors in the submission, but which do not force the algorithm to halt:
            - If the repository was not on `main` branch when submitted.
            - If the repository does not have a `main` branch, but an alternative was identified & successfully checked out (EG `master`).
            - If compulsory files are missing from the directory.
            - If unexpected files are missing from the directory.

        INFORMATION reports on other misc information obtained during the algorithm:
            - When optional files, or data files, are identified in a directory.
            - When a directory with a variable name is matched to a folder on the filesystem.
            - When optional folders are not found within the submission.
            - When optional subfolders with variable names are not matched to a folder on the filesystem.

        Returns the following values, in the order given, as a tuple:

        1. An AssignmentCheckerError instance that reports the FATAL error encountered. This value is None if no FATAL errors were encountered.
        2. A list of strings that contain the text to be issued by WARNINGs that the algorithm wants to issue.
        3. A list of strings that contain the text to be issued as INFORMATION.

        Note that if the first return value is None, and the second is an empty list, then the Directory instance is
        compatible with the directory on the filesystem that was passed in.

        `do_not_set_name` can be set to True to prevent variable-named folders from inheriting the pattern-matched
        name from the filesystem. This is exclusively used when attempting to match variable-named subdirectories
        to those on the filesystem.

        `substitutes_for_main_branch` should be a sequence of branch names that, if `main` is not present in
        the expected git repository, will be used instead.
        """
        WARNING = []
        INFORMATION = []

        if not directory.is_dir():
            return AssignmentCheckerError(f"Is not a directory: {directory}"), WARNING, INFORMATION

        # Check name
        name_before = self.name
        if not self.check_name(directory.stem, do_not_set_name=do_not_set_name):
            if self.variable_name:
                return (
                    AssignmentCheckerError(
                        f"Directory '{directory.stem}' does not have the expected form (expected to match '{self.name_pattern}')."
                    ),
                    WARNING,
                    INFORMATION,
                )
            else:
                return (
                    AssignmentCheckerError(
                        f"Directory {self.name} expected, but got name {directory.stem}."
                    ),
                    WARNING,
                    INFORMATION,
                )
        if self.name != name_before:
            INFORMATION.append(f"Matched '{directory.stem}' to pattern '{self.name_pattern}'.")

        # Check for presence (or absence) of git repository
        error, warnings = self.check_git_repo(directory, *substitutes_for_main_branch)
        if warnings:
            WARNING.append(warnings)
        if isinstance(error, AssignmentCheckerError):
            return error, WARNING, INFORMATION

        # Check the files that this folder contains.
        missing_compulsory, unexpected, optional = self.check_files(directory)
        if missing_compulsory:
            WARNING.append(
                f"Your submission is missing the following compulsory files (not found in {directory.stem}):\n"
                + "".join(f"\t{f}\n" for f in missing_compulsory)
            )
        if unexpected:
            WARNING.append(
                f"The following files were found in {directory.stem}, but were not expected:\n"
                + "".join(f"\t{f}\n" for f in unexpected)
            )
        if optional:
            INFORMATION.append(
                f"Found the following optional files inside {directory.stem}:\n"
                + "".join(f"\t{f}\n" for f in optional)
            )

        # Delegate further investigation down into subdirectories.
        # Handle non-variable-named directories.
        for subdir in self.fixed_name_subdirs:
            FATAL, s_warning, s_information = self.investigate_subdir(
                directory / subdir.name, subdir, do_not_set_name=do_not_set_name
            )
            WARNING.extend(s_warning)
            INFORMATION.extend(s_information)
            if FATAL is not None:
                return FATAL, WARNING, INFORMATION

        # Determine which folders on the filesystem represent the subdirectories that have variable names.
        matches, not_matched = self.match_variable_name_subdirs(directory)
        not_matched_and_compulsory = [s for s in not_matched if not s.is_optional]
        not_matched_and_optional = [s for s in not_matched if s.is_optional]
        INFORMATION.append(
            f"Matched the following directory patterns to the corresponding folders within {self.name}:\n"
            + "".join(
                f"\t{subdir.name_pattern} -> {dir_name}\n" for dir_name, subdir in matches.items()
            )
        )
        if not_matched_and_compulsory:
            return (
                AssignmentCheckerError(
                    f"Could not identify subdirectories in {self.name} whose names match the following patterns:\n\t"
                    + ", ".join(s.name_pattern for s in not_matched_and_compulsory)
                ),
                WARNING,
                INFORMATION,
            )
        if not_matched_and_optional:
            INFORMATION.append(
                f"The following optional folder patterns were not found in {self.name}:\n\t"
                + ", ".join(s.name_pattern for s in not_matched_and_optional)
            )
        # Then, actually go into these directories to continue the checking and logging.
        for path, subdir in matches.items():
            FATAL, s_warning, s_information = self.investigate_subdir(
                directory / path, subdir, do_not_set_name=do_not_set_name
            )
            WARNING.extend(s_warning)
            INFORMATION.extend(s_information)
            if FATAL is not None:
                return FATAL, WARNING, INFORMATION

        # Note that if we get to here, FATAL should be None.
        # But including this return here in case future developments add additional checks between
        # the variable-named directories and the end of the method.
        return None, WARNING, INFORMATION

    def check_files(self, directory: Path) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Check the files that are present in the directory, returning:

        1. A list of compulsory files that are missing.
        2. A list of files that were not expected to be found.
        3. A list of optional files that were found.
        """
        files = set(f for f in os.listdir(directory) if os.path.isfile(directory / f))

        missing_compulsory = set(self.compulsory) - files

        data_files = set(
            file for pattern in self.data_file_patterns for file in fnmatch.filter(files, pattern)
        )
        unexpected = files - set(self.compulsory) - set(self.optional) - data_files

        optional = files - unexpected - set(self.compulsory)

        return missing_compulsory, unexpected, optional

    def check_git_repo(
        self, directory: Path, *allowable_other_branches: str
    ) -> Tuple[AssignmentCheckerError | None, str | None]:
        """
        Check whether the folder on the filesystem is (or is not) a git repository, as expected by the instance.

        The method returns two values, in the following order.

        1. An AssignmentCheckerError (corresponding to a FATAL error in check_directories)
        in the following cases (otherwise None):
            - The instance expects a git repository on the filesystem, but does not detect one.
            - The instance expects a git repository on the filesystem, and a repository is present but...
                - There are untracked files in the repository.
                - There are unstaged changes to files in the repository.
                - There are uncommitted changes in the repository.
                - The repository could not checkout `main` or another of the `allowable_other_branches`.
            - The instance does not expect a git repository on the filesystem, but there is one.
        2. A string containing WARNING information, that can be passed back to `check_directories`.
            - None is returned if there are no warnings to record.
        """
        warning_info = None

        i_am_a_git_repo = is_git_repo(directory)
        if self.git_root:
            if not i_am_a_git_repo:
                return (
                    AssignmentCheckerError(f"Git repository not found at {directory}."),
                    None,
                )

            repo = git.Repo(directory)

            # Check working tree
            untracked_files, unstaged_files, uncommitted_files = is_clean(repo)
            if untracked_files:
                return (
                    AssignmentCheckerError(
                        f"You have untracked changes in your git repository: {untracked_files}"
                    ),
                    None,
                )
            elif unstaged_files:
                return (
                    AssignmentCheckerError(
                        f"You have unstaged changes in your git repository: {unstaged_files}"
                    ),
                    None,
                )
            elif uncommitted_files:
                return (
                    AssignmentCheckerError(
                        f"You have uncommitted changes in your git repository: {unstaged_files}"
                    ),
                    None,
                )

            # Switch to marking branch
            try:
                warning_info = switch_to_main_if_possible(repo, *allowable_other_branches)
            except AssignmentCheckerError as e:
                return e, None

            # Close repo to not interfere with other programs
            repo.close()
        elif i_am_a_git_repo:  # === (not self.git_repo and i_am_a_git_repo)
            return (
                AssignmentCheckerError(
                    f"Git repository found at {directory}, which is not the expected location."
                ),
                None,
            )

        return None, warning_info

    def check_name(self, directory_name: str, do_not_set_name: bool = False) -> bool:
        """
        Check that the directory name given is compatible with this instance.

        If self.variable_name is False, the directory_name must match self.name.
        If self.variable_name is True:
        - If self.variable_name_match is None, take the name provided as a match.
        - Otherwise, the directory_name must match the shell expression given in self.variable_name_match.

        In the case of a variable name and a matching directory name, the self.name
        property will be set to the matched value.
        This can be suppressed using the do_not_set_name input.
        """
        if not self.variable_name:
            return directory_name == self.name
        else:
            # Must match shell expression.
            if fnmatch.fnmatch(directory_name, self.name_pattern):
                if not do_not_set_name:
                    self.name = directory_name
                return True
            else:
                return False

    def investigate_subdir(
        self, path_to_subdir: Path, subdir: Directory, do_not_set_name: bool = False
    ) -> Tuple[AssignmentCheckerError | None, List[str], List[str]]:
        """
        Essentially wraps check_directory when called on a subdirectory on the instance.
        This has utility within check_directory() as we can refactor out the body of two `for` loops
        into this function;
        - When we investigate subdirectories with fixed names,
        - When we investigate subdirectories with variable names,
        after having matched these to folders on the filesystem.

        Note that `path_to_subdir` should point to the folder that is to be compared to `subdir`, unlike
        its counterpart in `check_directories` where `directory` points to the folder that is being compared to `self`.

        The returned values, and remaining arguments, are identical to those of `check_directory`.
        """
        warning = []
        information = []

        if not path_to_subdir.is_dir():
            if subdir.is_optional:
                information.append(
                    f"Optional subfolder '{subdir.name}' of '{self.name}' not found."
                )
                return None, warning, information
            else:
                return (
                    AssignmentCheckerError(
                        f"Expected subdirectory '{subdir.name}' to be present in '{self.name}', but it is not."
                    ),
                    warning,
                    information,
                )

        # Delegate checking to subdirectory
        FATAL, s_warning, s_information = subdir.check_against_directory(
            path_to_subdir, do_not_set_name=do_not_set_name
        )
        warning.extend(s_warning)
        information.extend(s_information)
        return FATAL, warning, information

    def match_variable_name_subdirs(
        self, directory: Path
    ) -> Tuple[Dict[str, Directory], List[Directory]]:
        """
        Handles cases where an instance has (potentially multiple) subdirectories
        that have variable names, meaning that we have to attempt to match directories
        based on their structure, not their names alone.

        The method will attempt to match compulsory directories first, before attempting
        to match optional directories (if any exist).

        The method returns two values, in the following order:

        1. A dictionary whose keys are the names of the subdirectories on the filesystem, and whose values are the Directory instances within self.subdirs that these match to.
        2. A list of Directories in self.subdirs that were not matched to directories on the filesystem.

        Note that the second return value potentially includes optional subdirectories.
        """
        possible_names = [
            subdir
            for subdir in os.listdir(directory)
            if os.path.isdir(directory / subdir)
            and subdir not in [fixed.name for fixed in self.fixed_name_subdirs]
        ]
        matches = {}
        not_matched = []

        # Attempt to match subdirectories to those available in the filesystem.
        # Create a list of all possible matches, for each subdirectory
        possible_matches_compulsory = {}
        possible_matches_optional = {}
        for subdir in self.variable_name_subdirs:
            compatible_directories: List[str] = []
            for pos_name in possible_names:
                fatal, warnings, _ = subdir.check_against_directory(
                    directory / pos_name, do_not_set_name=True
                )
                if (fatal is None) and (not warnings):
                    compatible_directories.append(pos_name)

            if subdir.is_optional:
                possible_matches_optional[subdir.name] = set(compatible_directories)
            else:
                possible_matches_compulsory[subdir.name] = set(compatible_directories)

        # Possible matches now maps the name of a subdir to a list of all
        # folders on the filesystem that it could match to.
        # Determine if there is a safe, unique mapping between all directories.
        all_are_mapped = match_to_unique_assignments(
            {**possible_matches_compulsory, **possible_matches_optional}
        )
        if all_are_mapped:
            # all_are_mapped maps subdir.name to a directory.
            # We need to flip this association and also provide subdir itself as the value.
            for subdir_name, matched_directory in all_are_mapped.items():
                matches[matched_directory] = [
                    subdir for subdir in self.variable_name_subdirs if subdir.name == subdir_name
                ][0]
        else:
            # We could not map all compulsory + optional subdirectories with variable names.
            # However, we can at least try to map the compulsory ones.
            not_matched = [s for s in self.variable_name_subdirs if s.is_optional]

            compulsory_are_matched = match_to_unique_assignments(possible_matches_compulsory)
            if compulsory_are_matched:
                for subdir_name, matched_directory in compulsory_are_matched.items():
                    matches[matched_directory] = [
                        subdir
                        for subdir in self.variable_name_subdirs
                        if subdir.name == subdir_name
                    ][0]
            else:
                not_matched = self.variable_name_subdirs

        return matches, not_matched
