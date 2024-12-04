from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Optional

from assignment_submission_checker.logging.log_entry import LogEntry
from assignment_submission_checker.logging.log_types import LogType


def heading(text: str, pad_above: int = 1) -> str:
    """
    Render a report heading.

    :param pad_above: Pad this many empty newlines above the title.
    """
    return "\n" * pad_above + f"{text}\n{'-' * len(text)}\n"


def relative_to_if_provided(path: Path, rel: Optional[Path] = None) -> Path:
    """
    Returns `path.relative_to(rel)` if `rel` is provided, otherwise returns `path`.
    """
    return path.relative_to(rel) if rel is not None else path


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
        return [e for e in self.entries if e.log_type.is_fatal]

    @property
    def information(self) -> List[LogEntry]:
        """
        Return all INFORMATION entries in the instance as a list, or an empty list if there are none.
        """
        return [e for e in self.entries if e.log_type.is_information]

    @property
    def warnings(self) -> List[LogEntry]:
        """
        Return all WARNINGS (of any kind) in the instance as a list, or an empty list if there are none.
        """
        return [e for e in self.entries if e.log_type.is_warning]

    def __init__(self, *entries: LogEntry, current_directory: Optional[Path] = None) -> None:
        """
        Initialise a Logger, optionally containing pre-existing entries.
        """
        self.current_directory = current_directory

        if not all(isinstance(e, LogEntry) for e in entries):
            raise ValueError("Pre-populated entries provided must be of type LogEntry")
        self.entries = list(entries)

    def add_entry(self, log_type: LogEntry | LogType, *content: str, **kwargs) -> None:
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

    def ignore_unexpected_files(
        self,
        ignore_patterns: Iterable[str],
        relative_to: Optional[Path] = None,
    ) -> List[LogEntry]:
        """
        Removes the given patterns from LogEntries that are warning about unexpected files.
        A file only needs to match a single pattern to be removed from the corresponding warnings.

        If a warning is left reporting no missing files, it is removed from the list of entries entirely.
        The return value of this function is a list of these (unedited) entries.

        :param relative_to: Shell expressions are considered relative to the given directory.
        :param ignore_patterns: Shell expressions to match to file names.
        """
        flag_for_removal = []
        for i, entry in enumerate(self.entries):
            if entry.log_type == LogType.WARN_UNEXPECTED_FILE:
                # Filter out ignore patterns, relative to given directory if necessary.
                where = entry.where.relative_to(relative_to) if relative_to else entry.where
                new_content = [
                    file
                    for file in entry.content
                    if not any(
                        fnmatch(f"{str(where)}/{file.strip()}", pattern)
                        for pattern in ignore_patterns
                    )
                    and file.strip()
                ]
                # If there is no content left in the entry, flag it for removal
                if not new_content:
                    flag_for_removal.append(i)
                else:
                    entry.content = new_content

        # Remove all warnings that now report nothing.
        # Do this by index, starting from the greatest index to avoid changing list indices
        # if we remove from the front
        have_been_removed = []
        for index in sorted(flag_for_removal, reverse=True):
            have_been_removed.append(self.entries.pop(index))
        return have_been_removed

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

    def parse(self, relative_to: Optional[Path] = None) -> str:
        """
        Parse all log entries into the output format, returning the formatted string.

        Output format provides a breakdown of FATAL, WARNINGS, and INFORMATION under three headings.
        The log entries should already be sorted into the order they were created,
        and thus be grouped in accordance with the directory tree.

        :param relative_to: Directory paths will be given relative to the given path, if provided.
        """
        report_string = heading("Validation Report", pad_above=0)

        for log_type, heading_text in zip(
            ("fatal", "warnings", "information"),
            ("FATAL: Errors in submission format", "WARNINGS", "INFORMATION"),
        ):
            entries: List[LogEntry] = getattr(self, log_type)
            if entries:
                report_string += heading(heading_text)
                for entry in entries:
                    report_string += entry.render(relative_to=relative_to)

        return report_string
