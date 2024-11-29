from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

import pytest

from assignment_submission_checker.utils import (
    copy_tree,
    match_to_unique_assignments,
    provide_tmp_directory,
)

if TYPE_CHECKING:
    from assignment_submission_checker.utils import Obj, Val


def print_passed_str(the_str: str) -> bool:
    return True if the_str == "foo" else False


SET_ERROR = RuntimeError("I always raise an error")


def always_raise_error() -> None:
    raise SET_ERROR


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
    [
        "function",
        "clean_on_error",
        "clean_on_success",
        "pass_as_arg",
        "error",
        "return_val",
        "function_call_args",
        "function_kwargs",
    ],
    [
        pytest.param(
            print_passed_str,
            True,
            True,
            None,
            None,
            True,
            ["foo"],
            None,
            id="Clean on success",
        ),
        pytest.param(
            print_passed_str,
            True,
            False,
            None,
            None,
            False,
            ["bar"],
            None,
            id="No clean on success",
        ),
        pytest.param(
            print_passed_str,
            True,
            True,
            "the_str",
            None,
            False,
            None,
            None,
            id="Pass as arg",
        ),
        pytest.param(
            always_raise_error,
            True,
            True,
            None,
            SET_ERROR,
            None,
            None,
            None,
            id="Cleanup on error",
        ),
        pytest.param(
            always_raise_error,
            False,
            True,
            None,
            SET_ERROR,
            None,
            None,
            None,
            id="No cleanup on error",
        ),
    ],
)
def test_provide_tmp_directory(
    tmp_path: Path,
    function: Callable[[Any], Any],
    clean_on_error: bool,
    clean_on_success: bool,
    pass_as_arg: Optional[str],
    error: Optional[Exception],
    return_val: Optional[Any],
    function_call_args: Optional[List[Any]],
    function_kwargs: Optional[Dict[str, Any]],
) -> None:
    if function_call_args is None:
        function_call_args = []
    if function_kwargs is None:
        function_kwargs = {}

    tmp_location = tmp_path / "test-provide-tmp-dir"

    @provide_tmp_directory(
        clean_on_error=clean_on_error,
        clean_on_success=clean_on_success,
        pass_dir_as_arg=pass_as_arg,
        where=tmp_location,
    )
    def wrapped(*args, **kwargs) -> None:
        return function(*args, **kwargs)

    if error is not None:
        with pytest.raises(type(error), match=str(error)):
            returned = wrapped(*function_call_args, **function_kwargs)

        if clean_on_error:
            assert not tmp_location.exists(), "TMP directory not cleaned on error."
        else:
            assert tmp_location.exists(), "TMP directory was cleaned on error."
    else:
        returned = wrapped(*function_call_args, **function_kwargs)

        if clean_on_success and error is None:
            assert not tmp_location.exists(), "TMP directory was not cleaned on success."
        elif not clean_on_success and error is None:
            assert tmp_location.exists(), "TMP directory was cleaned on success."

        assert return_val == returned, "Wrapped function did not return expected return value."


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
