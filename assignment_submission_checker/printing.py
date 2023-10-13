from typing import Literal

WARNING_HEADER = "_________\n! WARNING !"
ERROR_HEADER = "**********************\n!! ERROR !!"


def print_to_console(
    msg: str, *sub_msgs: str, type: Literal["log", "warn", "error"] = "log"
) -> None:
    """
    Prints information to the console in a standardised module-wide format.

    Sub-messages are printed on newlines with a tab indent.
    """

    if type == "warn":
        print(WARNING_HEADER)
    elif type == "error":
        print(ERROR_HEADER)

    # Print the messages themselves
    print(msg)
    for sub_message in sub_msgs:
        print(sub_message)

    if type == "warn":
        print("-" * len(WARNING_HEADER))
    elif type == "error":
        print("-" * len(ERROR_HEADER))

    return


def print_warning(msg: str, *sub_msgs: str) -> None:
    """
    Prints a warning to the console in a standardised module format.

    Wraps print_to_console with type set to "warn".
    """
    print_to_console(msg, *sub_msgs, type="warn")
    return


def print_error(msg: str, *sub_msgs: str) -> None:
    """
    Prints the string provided in a standardised module-wide error-format.
    """
    print_to_console(msg, *sub_msgs, type="error")
    return
