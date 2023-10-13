from pathlib import Path

from .assignment import Assignment
from .printing import print_error, print_to_console, print_warning


def check_archive_name(
    archive: Path, verbose: bool = True, expected_candidate_number: str = None
) -> None:
    """ """
    archive_name = archive.stem.split(".")[0]  # In case of multiple . characters

    # archive_name should be a candidate number,
    # so only numeric characters,
    # and 8 characters long
    if len(archive_name) != 8 or (not archive_name.isdigit()):
        print_warning(
            f"Your submission is named {archive_name}: this is not an 8-digit number.",
            "The archive should be named with your candidate number (8 digits), and no further characters.",
        )
    elif expected_candidate_number is not None:
        if archive_name != expected_candidate_number:
            print_warning(
                "Submission name and candidate number do not match.",
                f"Submission is named {archive_name} but your candidate number is {expected_candidate_number}.",
            )
        elif verbose:
            print_to_console(
                f"Candidate number {expected_candidate_number} matches submission folder name."
            )
    elif verbose:
        print_to_console(
            f"Submission folder name is valid.",
            f"NOTE: your candidate number was inferred as {archive_name}, please check this is the case.",
        )
    return


def check_submission(
    A: Assignment, archive_location: Path = None, ignore_extra_files: bool = False
) -> None:
    """ """
    # If provided with an archive location, set this as the target
    if archive_location is not None:
        A.set_target_archive(archive_location)

    # Extract submission archive
    A.extract_to_temp_dir()

    # Attempt to locate git repository
    found_repo, repo_is_clean, find_errors, clean_errors = A.check_for_git_root()
    if not found_repo:
        print_error(
            f"git repository was not found.",
            "A git repository was not found at the expected location in your submission",
            f"Encountered the following error: {find_errors}",
        )
    elif not repo_is_clean:
        print_warning(
            "Your git repository is not clean.",
            "There are untracked files and/or uncommitted changes present in your submission:",
            clean_errors,
        )

    # Attempt to validate expected files are present
    not_found, not_expected = A.search_for_missing_files()
    if not_found:
        print_error("The following files are missing from your submission:", *not_found)
    if not_expected and not ignore_extra_files:
        print_warning(
            "Unexpected files in submission.",
            "The following files were found in your submission, but were not expected. This might be intentional (EG you have additional data files for your tests), but please double check the list below:",
            *not_expected,
        )

    return
