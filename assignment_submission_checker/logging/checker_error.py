from typing import Optional

from assignment_submission_checker.logging.log_types import LogType


class AssignmentCheckerError(Exception):
    """
    Allows us to define a custom exception type for when the assignment checker
    encounters a genuine problem with the submission.

    :param entry: `LogType` that should be associated with the error.
    """

    entry: LogType

    def __init__(self, *args, log_as: Optional[LogType] = LogType.FATAL, **kwargs) -> None:
        """ """
        super().__init__(*args, **kwargs)

        self.entry = LogType(log_as)
