import argparse
import sys
from pathlib import Path

from . import __version__
from .checker import check_archive_name, check_archive_name_group, check_submission
from .printing import print_error, print_to_console
from .static import COMP0233_2324_A2 as CURRENT_ASSIGNMENT

DESCRIPTION = (
    f"A command-line tool to validate the format of your submission for assignment.\n"
    f"The current version validates according to the format specified for: {CURRENT_ASSIGNMENT.name}."
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
    parser.add_argument(
        "-i",
        "--ignore-extra-files",
        action="store_true",
        help="Suppress warnings about the presence of unexpected files in your submission. Use this option only if you are confident the only files you have added to your submission (on top of those explicitly requested by the assignment) are necessary data files, or images containing plots for your report (if a report is expected).",
    )
    parser.add_argument(
        "-c",
        "--check-cnumber",
        type=str,
        default=None,
        help="When checking the name of the submission file, additionally check that the submission name matches the candidate/group number provided. If not provided, the program always will still check that the submission name is in a valid format.",
    )

    args = parser.parse_args()

    if args.version:
        print_to_console(
            parser.prog,
            f"Version: {__version__}",
            f"Currently configured for: {CURRENT_ASSIGNMENT.name}",
        )

    if args.submission is not None:
        try:
            if CURRENT_ASSIGNMENT.group_assignment:
                check_archive_name_group(args.submission, expected_group_number=args.check_cnumber)
            else:
                check_archive_name(args.submission, expected_candidate_number=args.check_cnumber)

            check_submission(
                CURRENT_ASSIGNMENT,
                archive_location=args.submission,
                ignore_extra_files=args.ignore_extra_files,
            )
        except Exception as e:
            print_error(
                f"The assignment-checker encountered an error - please open an issue describing the circumstances that lead to this error:\n{str(e)}"
            )

    # Always attempt cleanup (is safe if directory does not exist)
    CURRENT_ASSIGNMENT.purge_tmp_dir()

    sys.exit(0)
