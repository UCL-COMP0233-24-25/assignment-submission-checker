from enum import IntEnum


class LogType(IntEnum):
    """ """

    FATAL = 0  # Catch-all for errors
    FATAL_NOT_A_DIR = 1  # Submission provided is not a directory
    FATAL_DIR_NAME_MATCH_PATTERN = 2  # Directory name expected to match pattern
    FATAL_DIR_NAME_MATCH_FIXED = 3  # Directory name doesn't match fixed name
    FATAL_NO_COMP_SUBDIR_MATCH = 4  # No compulsory subdirectory found with matching name pattern
    FATAL_NO_COMP_SUBDIR_MATCH_FIXED = 5  # Compulsory directory (fixed name) not found
    FATAL_NO_GIT_REPO = 6  # No git repo found (when there should be one)
    FATAL_GIT_UNTRACKED = 7  # Working tree not clean (untracked changes)
    FATAL_GIT_UNSTAGED = 8  # Working tree not clean (unstaged changes)
    FATAL_GIT_UNCOMMITTED = 9  # Working tree not clean (uncommitted files)
    FATAL_GIT_NO_VALID_BRANCH = 10  # No `main` branch or other acceptable branch name
    FATAL_GIT_CHECKOUT_FAILED = 11  # Could not checkout the correct branch ref
    FATAL_GIT_EXTRA_REPO = 12  # Git repository found and not expected

    WARN = 100  # Catch-all for warnings
    WARN_GIT_NOT_ON_MAIN = 101  # Repository was not left on main
    WARN_GIT_USES_MAIN_ALT = (
        102  # Repository has no main branch, but does have an allowable alternative
    )
    WARN_UNEXPECTED_FILE = 103  # No main but acceptable other branch
    WARN_FILE_NOT_FOUND = 104  # Compulsory file is missing

    INFO = 200  # Catch-all for information
    INFO_MATCHED_DIR_NAME = 201  # Matched pattern to directory name
    INFO_FOUND_OPTIONAL_FILE = 202  # Found optional file
    INFO_OPTIONAL_DIR_NOT_FOUND = 203  # Optional directory was not present
    INFO_MATCHED_OPT_DIR_PATTERNS = 204  # Matched optional directories to patterns
    INFO_OPTONAL_DIR_VARIABLE_NAME_NOT_FOUND = (
        205  # Optional subdirectory with a variable name was not present
    )

    @property
    def is_fatal(self) -> bool:
        """Whether the instance corresponds to a FATAL error."""
        return self < LogType.WARN

    @property
    def is_information(self) -> bool:
        """Whether the instance corresponds to INFORMATION."""
        return LogType.INFO <= self

    @property
    def is_warning(self) -> bool:
        """Whether the instance corresponds to a WARNING."""
        return LogType.WARN <= self < LogType.INFO
