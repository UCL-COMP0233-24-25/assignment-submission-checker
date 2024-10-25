from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

import pytest

from assignment_submission_checker.utils import copy_tree, match_to_unique_assignments

if TYPE_CHECKING:
    from assignment_submission_checker.utils import Obj, Val


@pytest.mark.parametrize(
    ["make_folder_structure", "copy", "destination", "into", "expected_error"],
    [
        pytest.param(
            "template_dir_dict",
            "top-level-folder",
            "new-top-level",
            True,
            None,
        ),
        pytest.param(
            "template_dir_dict",
            "top-level-folder",
            "new-top-level",
            False,
            None,
        ),
        pytest.param(
            "template_dir_dict",
            "i-dont-exist",
            "new-top-level",
            False,
            FileNotFoundError,
        ),
    ],
    indirect=["make_folder_structure"],
)
def test_copy_tree(
    make_folder_structure,
    tmp_path: Path,
    copy: Path,
    destination: Path,
    into: bool,
    expected_error: Optional[Exception],
) -> None:
    """Simple check that copy_tree works as intended."""
    copy, destination = Path(copy), Path(destination)

    copy = tmp_path / copy
    destination = tmp_path / destination

    if expected_error is not None:
        with pytest.raises(expected_error):
            copy_tree(copy, destination)
    else:
        copied_to = copy_tree(copy, destination, into=into)
        assert copied_to.is_dir()
        if into:
            assert copied_to == destination / copy.stem
        else:
            assert copied_to == destination


@pytest.mark.parametrize(
    ["input", "expected_answers"],
    [
        pytest.param(
            {
                "a": [1, 2, 3],
                "b": [3],
                "c": [2, 3],
            },
            {"a": 1, "b": 3, "c": 2},
            id="No recursion needed.",
        ),
        pytest.param(
            {
                "a": [1, 2, 3],
                "b": [1, 2, 3],
                "c": [3],
            },
            [
                {"a": 1, "b": 2, "c": 3},
                {"a": 2, "b": 1, "c": 3},
            ],
            id="2 possible solutions.",
        ),
        pytest.param(
            {
                "a": [1, 2, 3],
                "b": [1, 2, 3],
                "c": [1, 2, 3],
            },
            [
                {"a": 1, "b": 2, "c": 3},
                {"a": 1, "b": 3, "c": 2},
                {"a": 2, "b": 1, "c": 3},
                {"a": 2, "b": 3, "c": 1},
                {"a": 3, "b": 1, "c": 2},
                {"a": 3, "b": 2, "c": 1},
            ],
            id="Requires double recursion.",
        ),
        pytest.param(
            {
                "a": [1],
                "b": [1],
                "c": [2],
            },
            {},
            id="Failure case, no recursion.",
        ),
        pytest.param(
            {
                "a": [1, 2],
                "b": [1, 2],
                "c": [1, 2],
            },
            {},
            id="Failure case, involving recursion.",
        ),
    ],
)
def test_unique_assignments(input: Dict[Obj, List[Val]], expected_answers: List[Dict[Obj, Val]]):
    """ """
    if isinstance(expected_answers, dict):
        expected_answers = [expected_answers]

    answer = match_to_unique_assignments(input)

    found_a_valid_answer = False
    for possible_answer in expected_answers:
        if possible_answer == answer:
            found_a_valid_answer = True

    assert found_a_valid_answer, "An expected answer was not found."
