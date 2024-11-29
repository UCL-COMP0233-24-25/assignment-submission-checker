from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import List


class LogType(IntEnum):
    """ """

    FATAL = 1
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
            return self.__class__(self.log_type, self.where, self.content + other.content)

    def __post_init__(self) -> None:
        """
        - Casts to expected types for consistency.
        - Strip whitespace from content entries.
        - Remove duplicates from content entries.
        - Sorts content into alphabetical order.
        """
        if self.log_type not in LogType:
            raise ValueError(f"{self.log_type} is not a LogType")
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
