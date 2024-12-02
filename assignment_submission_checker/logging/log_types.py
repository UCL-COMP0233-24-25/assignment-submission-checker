from enum import IntEnum


class LogType(IntEnum):
    """ """

    FATAL = 0
    WARN_GIT = 1
    WARN_UNEXPECTED = 2
    WARN_NOT_FOUND = 3
    INFO = 4  # TSTK distinguish more types here to avoid string parsing as much as possible. Could also do this with the FATAL things
    # EG have FATAL be negative values, WARN_* be 100+x values, and INFO be 000-099 entries?


# FATALS:

# - Not a directory
# - Directory expected to match pattern
# - Directory name doesn't match fixed name
# - No subdirectory found matching pattern (compulsory subdirs)
# - Compulsory directory (non-variable name) not found
# - No git repo found (when there should be one)
# - Working tree not clean (untracked changes)
# - Working tree not clean (unstaged changes)
# - Working tree not clean (uncommitted files)
# - Could not locate the `main` branch or other acceptable branch name
# - Could not checkout the correct branch ref
# - Git repository found and not expected


# WARNINGS

# - Repository not on main
# - No main but acceptable other branch

# INFOS

# - Matched pattern to directory name
