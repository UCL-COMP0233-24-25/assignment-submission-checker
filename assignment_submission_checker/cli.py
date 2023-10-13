import argparse
from pathlib import Path
import sys

from . import __version__
from .checker import check_submission
from .static import COMP0233_2324_A1

CURRENT_ASSIGNMENT = COMP0233_2324_A1

DESCRIPTION = (
    f"A command-line tool to validate the format of your submission for assignment.\n"
    f"The current version validates according to the format specified for: {CURRENT_ASSIGNMENT.name}"
)


def cli():
    """ """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        "submission",
        type=Path,
        default=None,
        help="The (path to) the archive file that contains your submission.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display the current version number of this package, and the assignment that is currently configured in the output.",
    )

    args = parser.parse_args()

    if args.version:
        print("assignment-submission-checker")
        print(f"Version: {__version__}")
        print(f"Currently configured for: {CURRENT_ASSIGNMENT.name}")

    if args.submission is not None:
        try:
            check_submission(CURRENT_ASSIGNMENT, archive_location=args.submission)
        except Exception as e:
            print(
                f"The assignment-checker encountered an error - please open an issue describing the circumstances that lead to this error:\n{str(e)}"
            )

    # Always attempt cleanup (is safe if directory does not exist)
    CURRENT_ASSIGNMENT.purge_tmp_dir()

    sys.exit(0)
