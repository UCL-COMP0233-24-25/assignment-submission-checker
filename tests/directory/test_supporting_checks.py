from pathlib import Path
from typing import List, Optional, Set

import pytest

from assignment_submission_checker.directory import Directory
from assignment_submission_checker.logging.log_types import LogType


@pytest.mark.parametrize(
    [
        "name",
        "directory_name",
        "var_pattern",
        "do_not_change_name",
        "expected_result",
        "expected_name",
    ],
    [
        pytest.param(
            "Foobar",
            "Foobar",
            None,
            None,
            True,
            None,
            id="Non-variable, match",
        ),
        pytest.param(
            "Foobar",
            "Flibble",
            None,
            None,
            False,
            "Foobar",
            id="Non-variable, no match",
        ),
        pytest.param(
            "",
            "F00bar",
            "F??b*",
            None,
            True,
            None,
            id="Variable, match, set",
        ),
        pytest.param(
            "non-changing-name",
            "F00bar",
            "F??b*",
            True,
            True,
            "non-changing-name",
            id="Variable, match, not set",
        ),
        pytest.param(
            "",
            "F00bar",
            "Fl?bb*",
            None,
            False,
            "",
            id="Variable, no match",
        ),
    ],
)
def test_check_name(
    name: str,
    directory_name: str,
    var_pattern: Optional[str],
    do_not_change_name: bool,
    expected_result: bool,
    expected_name: Optional[str],
) -> None:
    """
    Tests the Directory.check_name method.

    expected_name will be set to the directory_name if not provided.
    """
    dir_dict = {"variable-name": var_pattern} if var_pattern is not None else {}
    if expected_name is None:
        expected_name = directory_name

    directory = Directory(name, dir_dict, None)

    result = (
        directory.check_name(directory_name, do_not_set_name=do_not_change_name)
        if do_not_change_name is not None
        else directory.check_name(directory_name)
    )

    assert result == expected_result, "Result of check_name does not match expected."
    assert (
        directory.name == expected_name
    ), "Directory's name has not been set to the expected value."


@pytest.mark.parametrize(
    [
        "make_folder_structure",
        "setup_folder_structure_with_git",
        "setup_submission",
        "allowable_other_branches",
        "dir_to_compare",
        "expected_entry_type",
        "subdir_to_check",
    ],
    [
        pytest.param(
            "template_dir_dict",
            {"rootdir": "top-level-folder/my-git-submission"},
            {},
            [],
            "top-level-folder/my-git-submission",
            None,
            "git-root-dir",
            id="Repo present, on main, no switch",
        ),
        pytest.param(
            "template_dir_dict",
            {"rootdir": "top-level-folder/my-git-submission"},
            {},
            [],
            "top-level-folder/my-git-submission/report",
            None,
            "git-root-dir/report",
            id="Not a repository folder, and no repository present.",
        ),
        pytest.param(
            "template_dir_dict",
            {"rootdir": "top-level-folder"},
            {},
            [],
            "top-level-folder",
            LogType.FATAL_GIT_EXTRA_REPO,
            ".",
            id="Git repo present when it shouldn't be.",
        ),
        pytest.param(
            "template_dir_dict",
            {
                "rootdir": "top-level-folder/my-git-submission",
                "checkout": "flibble",
            },
            {},
            [],
            "top-level-folder/my-git-submission",
            LogType.WARN_GIT_NOT_ON_MAIN,
            "git-root-dir",
            id="Wrong branch is checked out.",
        ),
        pytest.param(
            "template_dir_dict",
            {
                "rootdir": "top-level-folder/my-git-submission",
                "commit": "master",
            },
            {},
            ["flibble", "master", "foobar"],
            "top-level-folder/my-git-submission",
            LogType.WARN_GIT_USES_MAIN_ALT,
            "git-root-dir",
            id="Master in place of main, and acceptable.",
        ),
        pytest.param(
            "template_dir_dict",
            {
                "rootdir": "top-level-folder/my-git-submission",
                "commit": "master",
                "checkout": "foobar",
            },
            {},
            [],
            "top-level-folder/my-git-submission",
            LogType.FATAL_GIT_NO_VALID_BRANCH,
            "git-root-dir",
            id="No allowable references.",
        ),
        pytest.param(
            "template_dir_dict",
            {"rootdir": "top-level-folder/my-git-submission"},
            {"untracked": ["not_tracked.py"]},
            [],
            "top-level-folder/my-git-submission",
            LogType.FATAL_GIT_UNTRACKED,
            "git-root-dir",
            id="Untracked file.",
        ),
        pytest.param(
            "template_dir_dict",
            {"rootdir": "top-level-folder/my-git-submission"},
            {"unstaged": ["c1.py"]},
            [],
            "top-level-folder/my-git-submission",
            LogType.FATAL_GIT_UNSTAGED,
            "git-root-dir",
            id="Unstaged file.",
        ),
        pytest.param(
            "template_dir_dict",
            {"rootdir": "top-level-folder/my-git-submission"},
            {"uncommitted": ["c1.py"]},
            [],
            "top-level-folder/my-git-submission",
            LogType.FATAL_GIT_UNCOMMITTED,
            "git-root-dir",
            id="Uncommitted file.",
        ),
    ],
    indirect=[
        "make_folder_structure",
        "setup_folder_structure_with_git",
        "setup_submission",
    ],
)
def test_check_git_repo(
    setup_submission,
    tmp_path: Path,
    template_directory: Directory,
    allowable_other_branches: List[str],
    dir_to_compare: Path,
    expected_entry_type: Optional[LogType],
    subdir_to_check: str,
) -> None:
    """
    Runs check_git_repo on the template_directory[subdir_to_check] Directory instance,
    comparing it against the tmp_path / dir_to_compare folder location.
    """
    dir_to_compare = tmp_path / dir_to_compare
    assert dir_to_compare.is_dir(), f"{dir_to_compare} is not a directory!"

    git_log_entry = template_directory[subdir_to_check].check_git_repo(
        dir_to_compare, *allowable_other_branches
    )

    if expected_entry_type is not None:
        assert git_log_entry.log_type == expected_entry_type
    else:
        assert git_log_entry is None


@pytest.mark.parametrize(
    [
        "make_folder_structure",
        "dir_name",
        "expected_missing",
        "expected_unexpected",
        "expected_optional",
        "subdir_to_check",
    ],
    [
        pytest.param(
            "template_dir_dict",
            "top-level-folder/my-git-submission",
            [],
            [],
            [],
            "git-root-dir",
            id="Good file structure, (my-git-submission)",
        ),
        pytest.param(
            "bad_template_dir_dict",
            "top-level-folder/my-git-submission",
            ["c2.py"],
            [],
            [],
            "git-root-dir",
            id="Missing compulsory file, (my-git-submission)",
        ),
        pytest.param(
            "template_dir_dict",
            "top-level-folder/my-git-submission/report",
            [],
            [],
            ["AIUsage.md"],
            "git-root-dir/report",
            id="Good file structure, (my-git-submission/report)",
        ),
        pytest.param(
            "bad_template_dir_dict",
            "top-level-folder/my-git-submission/report",
            [],
            ["extra_image.png"],
            [],
            "git-root-dir/report",
            id="Unexpected file, (my-git-submission/report)",
        ),
        pytest.param(
            "template_dir_dict",
            "top-level-folder/my-git-submission/data",
            [],
            [],
            ["custom_data.csv"],
            "git-root-dir/data",
            id="Good file structure, (my-git-submission/data)",
        ),
        pytest.param(
            "bad_template_dir_dict",
            "top-level-folder/my-git-submission/data",
            [],
            ["wrong_format.json"],
            ["good_format.csv"],
            "git-root-dir/data",
            id="Unexpected .json file, my-git-submission/data",
        ),
    ],
    indirect=["make_folder_structure"],
)
def test_check_files(
    make_folder_structure,
    tmp_path: Path,
    dir_name: str,
    expected_missing: Set[str],
    expected_unexpected: Set[str],
    expected_optional: Set[str],
    subdir_to_check: str,
    template_directory: Directory,
) -> None:
    if isinstance(expected_missing, list):
        expected_missing = set(expected_missing)
    if isinstance(expected_unexpected, list):
        expected_unexpected = set(expected_unexpected)
    if isinstance(expected_optional, list):
        expected_optional = set(expected_optional)

    logger = template_directory[subdir_to_check].check_files(tmp_path / dir_name)

    missing_files = [
        entry for entry in logger.warnings if entry.log_type == LogType.WARN_FILE_NOT_FOUND
    ]
    unexpected_files = [
        entry for entry in logger.warnings if entry.log_type == LogType.WARN_UNEXPECTED_FILE
    ]
    optional_files = [
        entry for entry in logger.information if entry.log_type == LogType.INFO_FOUND_OPTIONAL_FILE
    ]

    if expected_missing:
        assert len(missing_files) == 1
        assert (
            set(missing_files[0].content) == expected_missing
        ), "Not all missing files were flagged."
    else:
        assert len(missing_files) == 0

    if unexpected_files:
        assert len(unexpected_files) == 1
        assert (
            set(unexpected_files[0].content) == expected_unexpected
        ), "Not all unexpected files were identified."
    else:
        assert len(unexpected_files) == 0

    if optional_files:
        assert len(optional_files) == 1
        assert (
            set(optional_files[0].content) == expected_optional
        ), "Optional files were incorrectly identified."
    else:
        assert len(optional_files) == 0
