from pathlib import Path

from .assignment import Assignment
from .printing import print_error, print_to_console, print_warning


def check_archive_name(
    archive: Path, verbose: bool = True, expected_candidate_number: str = None
) -> bool:
    """ """
    archive_name = archive.stem.split(".")[0]  # In case of multiple . characters
    name_is_ok = True

    # archive_name should be a candidate number,
    # so only numeric characters,
    # and 8 characters long
    if len(archive_name) != 8 or (not archive_name.isdigit()):
        print_warning(
            f"Your submission is named {archive_name}: this is not an 8-digit number.",
            "The archive should be named with your candidate number (8 digits), and no further characters.",
        )
        name_is_ok = False
    elif expected_candidate_number is not None:
        if archive_name != expected_candidate_number:
            print_warning(
                "Submission name and candidate number do not match.",
                f"Submission is named {archive_name} but your candidate number is {expected_candidate_number}.",
            )
            name_is_ok = False
        elif verbose:
            print_to_console(
                f"Candidate number {expected_candidate_number} matches submission folder name."
            )
    elif verbose:
        print_to_console(
            f"Submission folder name is valid.",
            f"NOTE: your candidate number was inferred as {archive_name}, please check this is the case.",
        )

    return name_is_ok


def check_archive_name_group(
    archive: Path, verbose: bool = True, expected_group_number: str = None
) -> bool:
    """ """
    archive_name = archive.stem.split(".")[0]  # In case of multiple . characters
    name_is_ok = True

    # archive_name should match working_group_XX.tar.gz
    # XX might have special characters, in which case we need to catch those
    split_archive_name = archive_name.split("_")
    group_id = split_archive_name[-1]

    # We also need to check if the expected group number was input as a single digit or not
    # They should use the 2-digit code, but just in case we will catch
    if expected_group_number is not None:
        if expected_group_number.isdigit() and len(expected_group_number) == 1:
            print_warning(
                f"You have provided your expected group number as {expected_group_number} - this is not a 2-digit number.",
                f"The checker will continue, but will be using an expected group number of {'0' + expected_group_number}",
                f"We recommend you pass in the full group number (with leading zeros) in future.",
            )
            expected_group_number = "0" + expected_group_number

    if (
        (split_archive_name[0] != "working")
        or (split_archive_name[1] != "group")
        or (len(split_archive_name) != 3)
    ):
        print_warning(
            f"Your submission is named {archive_name}: this does not match the pattern working_group_XX",
        )
        name_is_ok = False
    elif group_id.isdigit() and len(group_id) == 1:
        print_warning(
            f"Your group number is provided as a single digit ({group_id}).",
            "For group numbers less than 10, you should append a leading 0 to your group number to match the pattern pattern working_group_XX",
        )
        name_is_ok = False
    elif expected_group_number is not None:
        if group_id != expected_group_number:
            print_warning(
                "Submission name and group number do not match.",
                f"Submission is named {archive_name} but your group number is {expected_group_number}.",
            )
            name_is_ok = False
        elif verbose:
            print_to_console(
                f"Group number {expected_group_number} matches submission folder name."
            )
    elif verbose:
        print_to_console(
            f"Submission folder name is valid.",
            f"NOTE: your group number was inferred as {group_id}, please check this is the case.",
        )

    return name_is_ok


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
    if A.group_assignment and (not_expected and not ignore_extra_files):
        # In the group assignment, there is more freedom, so phrase the unexpected files a bit more gently.
        print_warning(
            "The following files were included in your submission.",
            "Please check that you expect them to be there:",
            *not_expected,
        )
    if (not A.group_assignment) and (not_expected and not ignore_extra_files):
        # In individual coursework, structure is more strict. Phrase extra files message a bit more harshly.
        print_warning(
            "Unexpected files in submission.",
            "The following files were found in your submission, but were not expected. This might be intentional (EG you have additional data files for your tests), but please double check the list below:",
            *not_expected,
        )

    return
