import os
import stat
from pathlib import Path
from typing import Callable


def on_readonly_error(f: Callable[[Path], None], path: Path, exc_info) -> None:
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file) it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=on_readonly_error)``
    """
    # Attempt multiple times to allow os time to close references
    for _ in range(50):
        try:
            os.chmod(path, stat.S_IWRITE)
            f(path)
        except:
            pass
