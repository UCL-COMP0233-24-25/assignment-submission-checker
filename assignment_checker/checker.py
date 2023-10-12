from .assignment import Assignment


def check_submission(A: Assignment) -> None:
    """ """
    # Extract submission archive
    A.extract_to_temp_dir()

    # Attempt to locate git repository
    found_repo, repo_is_clean, find_errors, clean_errors = A.check_for_git_root()
    if not found_repo:
        print(
            f"git repository was not found at the expected location in your submission (encountered the following error):\n\t{find_errors}"
        )
    elif not repo_is_clean:
        print(
            f"There are untracked files and/or uncommitted changes present in your submission:\n\t{clean_errors}"
        )

    # Attempt to validate expected files are present
    not_found, not_expected = A.search_for_missing_files()
    if not_found:
        print("The following files are missing from your submission:")
        for file in not_found:
            print(f"\t{file}")
    if not_expected:
        print(
            "The following files were found in your submission, but were not expected. This might be intentional (EG you have additional data files for your tests), but please double check the list below:"
        )
        for file in not_expected:
            print(f"\t{file}")

    return
