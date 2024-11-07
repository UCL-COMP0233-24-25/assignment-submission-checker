from pathlib import Path

from assignment_submission_checker.directory import Directory


def test_init(template_directory: Directory):
    placeholder_name = "structure"
    path_to_repo = "git-root-dir"
    path_to_data = "git-root-dir/data"

    # Manual validation of what was read in
    assert template_directory.name == placeholder_name
    assert not template_directory.compulsory
    assert not template_directory.optional
    assert not template_directory.is_optional
    assert not template_directory.data_file_patterns
    assert template_directory.variable_name
    assert template_directory.path_from_root == Path(".")
    assert len(template_directory.subdirs) == 1

    # Validate that we can fetch children via reference
    repo_directory = template_directory[path_to_repo]

    assert repo_directory.git_root
    assert {"c1.py", "c2.py"} == set(repo_directory.compulsory)
    assert {"notebook.ipynb", "provided_code.py"} == set(repo_directory.optional)
    assert repo_directory.path_from_root == Path(path_to_repo)
    assert len(repo_directory.subdirs) == 2
    assert repo_directory.parent is template_directory

    # Validate that we can fetch children via path ref
    data_dir = template_directory[path_to_data]

    assert (
        data_dir.is_optional
    ), "No compulsory files (nor subdirs to recurse into) should imply directory is optional"
    assert data_dir.path_from_root == Path(path_to_data)
    assert data_dir.parent is repo_directory


def test_traverse(template_directory: Directory) -> None:
    expected_order = [
        "structure",
        "git-root-dir",
        "data",
        "report",
    ]

    for expected_name, dir in zip(expected_order, template_directory):
        assert expected_name == dir.name, "Out-of-order-iteration through file structure!"
