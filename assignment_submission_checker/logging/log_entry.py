from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from assignment_submission_checker.logging.log_types import LogType


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

    @property
    def content_as_bullets(self) -> str:
        """Renders self.contents as items in a bulleted list."""
        return "\n".join(f"- {item}" for item in self.content)

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
        - Cast to expected types, including making a clean reference for `content`.
        - Strip whitespace from content entries.
        - Remove duplicates from content entries.
        - Sorts content into alphabetical order.
        """
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

    def render(self, relative_to: Optional[Path] = None) -> str:
        """
        Converts the instance into a string that can be written to the output.

        :param relative_to: Directory paths will be given relative to this directory, if provided.
        """
        where = self.where.relative_to(relative_to) if relative_to else self.where
        output_str = ""

        match self.log_type:
            # FATALS
            case LogType.FATAL_NOT_A_DIR:
                output_str = f"{where} is not a directory"
            case LogType.FATAL_DIR_NAME_MATCH_PATTERN:
                output_str = f"Directory '{where}' does not have the expected form (expected to match '{where.parent}/{self.content[0]}')."
            case LogType.FATAL_DIR_NAME_MATCH_FIXED:
                output_str = (
                    f"Directory ({where.parent}/){self.content[0]} expected, but got {where}."
                )
            case LogType.FATAL_NO_GIT_REPO:
                output_str = f"No git repository found at {where}."
            case LogType.FATAL_GIT_UNTRACKED:
                output_str = (
                    f"Untracked changes present in git repository ({where}):\n"
                    + self.content_as_bullets
                )
            case LogType.FATAL_GIT_UNSTAGED:
                output_str = (
                    f"Unstaged changes present in git repository ({where}):\n"
                    + self.content_as_bullets
                )
            case LogType.FATAL_GIT_UNCOMMITTED:
                output_str = (
                    f"Unstaged changes present in git repository ({where}):\n"
                    + self.content_as_bullets
                )
            case LogType.FATAL_GIT_NO_VALID_BRANCH:
                output_str = (
                    f"Repository {where} has no 'main' branch, nor any acceptable alternative."
                )
            case LogType.FATAL_GIT_CHECKOUT_FAILED:
                output_str = f"Could not checkout branch {self.content[0]} in repository {where}."
            case LogType.FATAL_GIT_EXTRA_REPO:
                output_str = f"Found a repository at {where}, but did not expect to."
            case LogType.FATAL_NO_COMP_SUBDIR_MATCH_FIXED:
                output_str = f"Compulsory subdirectory {where}/{self.content[0]} was not found."
            case LogType.FATAL_NO_COMP_SUBDIR_MATCH:
                output_str = (
                    f"Failed to find compulsory subdirectories matching patterns in {where}:\n"
                ) + self.content_as_bullets
            # WARNINGS
            case LogType.WARN_GIT_NOT_ON_MAIN:
                output_str = f"Repository {where} was not on 'main' branch."
            case LogType.WARN_GIT_USES_MAIN_ALT:
                output_str = (
                    f"Repository {where} does not have a 'main' branch,"
                    f"but found {self.content[0]}, which is an acceptable alternative."
                )
            case LogType.WARN_FILE_NOT_FOUND:
                output_str = (
                    f"The following compulsory files were not found in {where}:\n"
                    + self.content_as_bullets
                )
            case LogType.WARN_UNEXPECTED_FILE:
                output_str = (
                    f"The following files were found, but not expected, in {where}:\n"
                    + self.content_as_bullets
                )
            # INFORMATION
            case LogType.INFO_MATCHED_DIR_NAME:
                output_str = (
                    f"Matched '({where.parent}/){where.stem}' to pattern '{self.content[0]}'."
                )
            case LogType.INFO_FOUND_OPTIONAL_FILE:
                output_str = (
                    f"The following optional files were found in {where}:\n"
                    + self.content_as_bullets
                )
            case LogType.INFO_OPTIONAL_DIR_NOT_FOUND:
                output_str = f"Optional directory ({where}/){self.content[0]} not found."
            case LogType.INFO_MATCHED_OPT_DIR_PATTERNS:
                output_str = (
                    f"Matched the following patterns to subdirectories in {where}:\n"
                    + self.content_as_bullets
                )
            case LogType.INFO_OPTONAL_DIR_VARIABLE_NAME_NOT_FOUND:
                output_str = (
                    f"The following optional folder patterns were not found in {where}:\n"
                    + self.content_as_bullets
                )
            case _:
                raise TypeError(f"Rendering not supported for {self.log_type}.")
        return output_str + "\n"
