import argparse
import sys
from pathlib import Path
from warnings import warn

from . import __version__
from .cli_main import ASSIGNMENT_SPEC_REFERENCES, main

DESCRIPTION = (
    "A command-line tool to validate the format of your submission for a COMP0233 assignment. "
    "The checker requires an internet connection, unless: "
    "you use the -l or --local-specs option to provide the assignment specification file (.json) locally, "
    "AND do not use the -g or --github-clone option to request the checker clone your submission from GitHub."
)


class CLIParser(argparse.ArgumentParser):
    """
    A custom subclass of argparse.ArgumentParser,
    which changes the default behaviour on an error in CLI parsing to print the
    command-line help, as opposed to throwing an error to stderr.
    """

    def error(self, message):
        self.print_help_and_exit(msg=message)

    def print_help_and_exit(self, msg: str = "", code: int = 2) -> None:
        """
        Have the parser print the command-line help before exiting with the code provided.

        An optional message `msg` can be provided, and will be printed to the screen prior to
        displaying the help.
        'Refer to CLI usage below' will automatically be appended to this message.
        """
        sys.stderr.write(f"{msg}\nRefer to CLI usage below:\n\n")
        self.print_help()
        sys.exit(2)


def cli():
    """CLI handle for the assignment submission checker package."""
    parser = CLIParser(description=DESCRIPTION)

    parser.add_argument(
        "-g",
        "--github-clone",
        action="store_true",
        help="Clone your submission from github, rather than checking against a local copy. "
        "IF YOU USE this option, your input to the `submission` argument should be the HTTPS or SSH "
        "clone URL for your submission repository on GitHub classroom. "
        "Using this option requires an internet connection, and uses your system's git configuration.",
    )
    parser.add_argument(
        "-l",
        "--local-specs",
        action="store_true",
        help="Read assignment specifications from a local file, rather than fetching from the internet. "
        "If you have previously downloaded one of the assignment specifications onto your computer, "
        "you can use this option to run the checker on a local copy of your submission, "
        "without an internet connection. "
        "IF YOU USE this option, your input to the `assignment` argument should be the file path to a "
        "local copy of the assignment specification (.json) you wish to read in. ",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default=None,
        help="Redirect any (text) output to the given location.",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress printouts to the console. "
        "You must provide the -o or --output-file value to use this option, "
        "otherwise the information gathered by the checker will not be saved or displayed.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display the current version number of this package.",
    )
    parser.add_argument(
        "assignment",
        help="The assignment specification YYYY-assignment_id to validate the submission against, "
        "or the path to the specification file if using the -l or --local-specs option. "
        f"See {ASSIGNMENT_SPEC_REFERENCES}/README.md for an explanation of the YYYY-assignment_id format, "
        f"and {ASSIGNMENT_SPEC_REFERENCES} for a list of available assignment specifications.",
        nargs=1,
        type=str,
    )
    parser.add_argument(
        "submission",
        help="Path to your submission folder, "
        "or the HTTPS / SSH clone link of your GitHub classroom repository if using the -g or --github-clone option.",
        nargs=1,
        type=str,
    )

    args = parser.parse_args()
    args_to_main = {}

    if args.version:
        print(f"{parser.prog}, {__version__}")
        sys.exit(0)
    args.assignment = args.assignment[0]
    args.submission = args.submission[0]

    # Check that we can actually produce the output
    if args.quiet and (args.output_file is None):
        parser.print_help_and_exit(
            msg="You have suppressed console output but have not provided an alternative output location."
        )
    elif args.output_file is not None:
        args.output_file = args.output_file[0]

    # Check that the supposed local copy of the file is actually exists if we are being asked to use it.
    if args.local_specs:
        local_specs = Path(args.assignment)
        if not local_specs.is_file():
            parser.print_help_and_exit(
                f"The file {local_specs} that contains the assignment specification does not exist."
            )
        warn(
            f"Reading assignment specifications from local file {local_specs}; "
            "you should check this file is up-to-date before you submit."
        )
        args_to_main["local_specs"] = local_specs
    else:
        # We will need to download the specification file from GitHub
        args_to_main["assignment_lookup"] = str(args.assignment)

    # Do we need to clone from github, or check against a local repository
    if args.github_clone:
        args_to_main["github_clone_url"] = args.submission
    else:
        submission_path = Path(args.submission)
        if not submission_path.exists():
            parser.print_help_and_exit(
                f"The path {submission_path} that you have provided as your submission does not exist."
            )
        args_to_main["submission"] = Path(args.submission)

    # Call main() to actually run the checks
    string_output = main(**args_to_main)

    # Write to stdout if not running quietly
    if not args.quiet:
        sys.stdout.write(string_output)
    # Write to file buffer if requested
    if args.output_file:
        with open(Path(args.output_file), "w") as f:
            f.write(string_output)

    sys.exit(0)
