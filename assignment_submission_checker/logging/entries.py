from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import List

from assignment_submission_checker.utils import AssignmentCheckerError


class LogType(IntEnum):
    """ """

    FATAL = 0
    WARN_GIT = 1
    WARN_UNEXPECTED = 2
    WARN_NOT_FOUND = 3
    INFO = 4


@dataclass
class LogEntry:
    """
    Stores:

    (abs path to) directory in which log entry was recorded
    log type
    string content (as individual items) that make up the entry
    """

    log_type: LogType
    where: Path
    content: List[str] = field(default_factory=lambda: [])

    def __add__(self, other: LogEntry) -> LogEntry:
        """
        The sum of two compatible `LogEntry`s is the combination of their content.

        If `other` is not a `LogEntry` with the same `log_type` and `where` attribute,
        the two values cannot be summed.
        """
        if self._same_reference(other):
            return self.__class__(
                self.log_type, where=self.where, content=self.content + other.content
            )
        elif self.log_type != other.log_type:
            err_str = (
                "Log types are not compatible " f"(self: {self.log_type}, other {other.log_type})"
            )
        else:
            err_str = (
                "Logs do not refer to same location " f"(self {self.where}, other {other.where})"
            )
        raise TypeError(err_str)

    def __post_init__(self) -> None:
        """
        If log_type is an AssignmentCheckerError, then create a FATAL instance from it.

        Otherwise;
        - Cast to expected types, including making a clean reference for `content`.
        - Strip whitespace from content entries.
        - Remove duplicates from content entries.
        - Sorts content into alphabetical order.
        """
        # Create from an AssignmentCheckerError if provided.
        if isinstance(self.log_type, AssignmentCheckerError):
            self.content.insert(0, str(self.log_type))
            self.log_type = LogType.FATAL
        else:
            # This will raise a TypeError if casting cannot occur, as we expect.
            self.log_type = LogType(self.log_type)

        self.where = Path(self.where)

        if isinstance(self.content, str):
            self.content = [self.content]
        else:
            self.content = list(self.content)
        self._format_content()

    def _format_content(self) -> None:
        """
        Strips whitespace, removes duplicates, and sorts `self.content` into alphabetical order.

        Note that duplicates are removed after stripping whitespace.
        """
        self.content = sorted(set(text.strip() for text in self.content))

    def _same_reference(self, other: LogEntry) -> bool:
        """
        Two `LogEntries` may point to the same directory (`where`) and be of the same `log_type`.
        Return `True` if this is the case, otherwise return `False`.

        In the event that this method returns `True`, the two entries can be summed.
        """
        if not isinstance(other, LogEntry):
            raise TypeError(f"{other} is not a {self.__class__} object")
        return self.log_type == other.log_type and self.where == other.where

    def add_content(self, *content_items: str) -> None:
        """
        Add additional content items to this instance.

        Any content items that are duplicates of entries already in the instance will not be added.
        """
        self.content.extend(content_items)
        self._format_content()
