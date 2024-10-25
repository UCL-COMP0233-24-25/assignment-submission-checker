from pathlib import Path

import pytest

from assignment_submission_checker.assignment import Assignment


@pytest.mark.parametrize(
    ["via_text"],
    [pytest.param(True, id="From file"), pytest.param(False, id="From json string")],
)
def test_creation(template_json: Path, via_text: bool) -> None:
    if via_text:
        with open(template_json, "r") as f:
            content = f.read()
        assignment = Assignment.from_json(json_str=content)
    else:
        assignment = Assignment.from_json(file=template_json)

    # Should inherit default branch
    assert assignment.git_branch_to_mark == "main"
    # Should autofill to 2 characters in the number
    assert assignment.id == "009"
    # No title was given
    assert assignment.title == "<No title given>"
    # Academic year should fill correctly
    assert assignment.academic_year == "1994-1995"

    # Directory structure should be taking the name root.
    assert assignment.directory_structure.name == "root"
