from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from assignment_submission_checker.logging.entries import LogEntry, LogType
from assignment_submission_checker.utils import AssignmentCheckerError


class Logger:
    """
    Store entries as we go through the checking process
    """

    _current_directory: str
    entries: List[LogEntry]

    @property
    def current_directory(self) -> Path:
        """
        Current path being pointed to by the Logger.

        All `LogEntry`s created without explicitly passing the `where` argument will have it
        default to this directory.
        """
        return self._current_directory

    @current_directory.setter
    def current_directory(self, new_value: str | None | Path) -> None:
        if new_value:
            self._current_directory = Path(new_value)
        else:
            self._current_directory = None

    @property
    def fatal(self) -> List[LogEntry]:
        """
        Return all FATAL entries in the instance as a list, or an empty list if there are none.
        """
        return [e for e in self.entries if e.log_type == LogType.FATAL]

    @property
    def warnings(self) -> List[LogEntry]:
        """
        Return all WARNINGS (of any kind) in the instance as a list, or an empty list if there are none.
        """
        return [e for e in self.entries if e.log_type not in [LogType.FATAL, LogType.INFO]]

    def __init__(self, *entries: LogEntry, current_directory: Optional[Path] = None) -> None:
        """
        Initialise a Logger, optionally containing pre-existing entries.
        """
        self.current_directory = current_directory

        if not all(isinstance(e, LogEntry) for e in entries):
            raise ValueError("Pre-populated entries provided must be of type LogEntry")
        self.entries = list(entries)

    def add_entry(
        self, log_type: AssignmentCheckerError | LogEntry | LogType, *content: str, **kwargs
    ) -> None:
        """
        Add an entry to the instance.

        `args` and `kwargs` are passed to LogEntry.__init__.
        """
        if "where" not in kwargs and self.current_directory:
            kwargs["where"] = self.current_directory

        if isinstance(log_type, LogEntry):
            self.entries.append(log_type)
        else:
            self.entries.append(LogEntry(log_type=log_type, content=content, **kwargs))

    def add_info(self, *content: str, **kwargs) -> None:
        """
        Add a LogType.INFO entry to the instance, with the given content.

        `kwargs` are passed to LogEntry.__init__.
        """
        self.add_entry(LogType.INFO, *content, **kwargs)

    def include(self, other: Logger) -> None:
        """
        Include the other `Logger`'s entries in the instance's.

        Note that whilst this provides a shorthand for combining logs, note that `self.current_directory` is preserved.
        As such, take care when using this method to combine `Logger`s,
        if you are relying on the `current_directory` property.
        """
        if not isinstance(other, Logger):
            raise TypeError(f"Can only include another Logger instance, not {type(other)}")
        self.entries.extend(other.entries)
