import os
import stat
from pathlib import Path
from typing import Callable


class AssignmentCheckerError(Exception):
    """
    Allows us to define a custom exception type for when the assignment checker
    encounters a genuine problem with the submission.
    """


def on_readonly_error(f: Callable[[Path], None], path: Path, exc_info) -> None:
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file) it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=on_readonly_error)``
    """
    os.chmod(path, stat.S_IWRITE)
    f(path)
