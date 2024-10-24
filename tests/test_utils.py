from typing import Dict, List

import pytest

from assignment_submission_checker.utils import Obj, Val, match_to_unique_assignments


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
