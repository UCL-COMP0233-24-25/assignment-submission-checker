import re
from pathlib import Path
from typing import List

import pytest

from assignment_submission_checker.logging.entries import LogEntry, LogType
from assignment_submission_checker.utils import AssignmentCheckerError


def test_init() -> None:
    # Can create with each type of LogType
    for log_type in LogType:
        LogEntry(log_type, ".")

    # Cannot create passing in nonsense
    with pytest.raises(ValueError):
        LogEntry("flibble", ".")

    # Casting strings to paths
    p = Path("foo/bar")
    assert LogEntry(LogType.FATAL, where=str(p)).where == p

    # Duplicate content is removed
    # And content is sorted
    content = ("0", "2", "1", "0", "3")
    formatted_content = ["0", "1", "2", "3"]
    assert LogEntry(LogType.FATAL, where=".", content=content).content == formatted_content

    # Can be created from an AssignmentCheckerError
    from_error = LogEntry(AssignmentCheckerError("Error message"), where=".")
    assert from_error.log_type == LogType.FATAL
    assert from_error.content == ["Error message"]


@pytest.mark.parametrize(
    ["left", "right", "expected"],
    [
        pytest.param(
            LogEntry(LogType.FATAL, where="."),
            LogEntry(LogType.INFO, where="."),
            TypeError("Log types are not compatible"),
            id="Different log types",
        ),
        pytest.param(
            LogEntry(LogType.FATAL, where="."),
            LogEntry(LogType.FATAL, where="foo/bar"),
            TypeError("Logs do not refer to same location"),
            id="Different directories referenced",
        ),
        pytest.param(
            LogEntry(LogType.FATAL, where=".", content=["0", "2"]),
            LogEntry(LogType.FATAL, where=".", content=["1", "0"]),
            ["0", "1", "2"],
            id="Content is concatenated, without duplicates.",
        ),
    ],
)
def test_compare_and_add(left: LogEntry, right: LogEntry, expected: Exception | List[str]) -> None:
    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=re.escape(str(expected))):
            left + right
    else:
        computed = left + right

        assert computed == LogEntry(left.log_type, left.where, expected)
        assert computed == LogEntry(right.log_type, right.where, expected)
