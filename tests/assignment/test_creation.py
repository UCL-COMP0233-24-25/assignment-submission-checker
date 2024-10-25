from pathlib import Path

from assignment_submission_checker.assignment import Assignment


def test_creation(template_json: Path) -> None:
    assignment = Assignment.from_json(template_json)

    # Should inherit default branch
    assert assignment.git_branch_to_mark == "main"
    # Should autofill to 2 characters in the number
    assert assignment.id == "09"
    # No title was given
    assert assignment.title == "<No title given>"
    # Academic year should fill correctly
    assert assignment.academic_year == "1994-1995"

    # Directory structure should be taking the name root.
    assert assignment.directory_structure.name == "root"
