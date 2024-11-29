from __future__ import annotations

from typing import List

from assignment_submission_checker.logging.entries import LogEntry, LogType


class Logger:
    """
    Store entries as we go through the checking process
    """

    entries: List[LogEntry]

    def __init__(self, *entries: LogEntry) -> None:
        """
        Initialise a Logger, optionally containing pre-existing entries.
        """
        if not all(isinstance(e, LogEntry) for e in entries):
            raise ValueError("Pre-populated entries provided must be of type LogEntry")
        self.entries = list(entries)
