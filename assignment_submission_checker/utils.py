import os
import stat
import shutil
from copy import deepcopy
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar

Obj = TypeVar("Object")
Val = TypeVar("Value")


class AssignmentCheckerError(Exception):
    """
    Allows us to define a custom exception type for when the assignment checker
    encounters a genuine problem with the submission.
    """


def copy_tree(
    src: Path,
    dest: Path,
    into: bool = False,
) -> Path:
    """
    Copies the directory tree to the location on the filesystem.

    Returns the path to the copied tree.

    :param src: Root directory whose tree should be copied.
    :param dest: Path to the copy destination.
    :param into: If True, then src will be copied into dest, under the name dest / src.stem, rather than directly to the destination location.
    """
    if isinstance(src, str):
        src = Path(src)
    if isinstance(dest, str):
        dest = Path(dest)

    if into:
        dest = dest / src.stem

    shutil.copytree(src, dest, symlinks=False, dirs_exist_ok=False)

    return dest


def match_to_unique_assignments(possible_mappings: Dict[Obj, Set[Val]]) -> Dict[Obj, Val]:
    """
    Given a set of objects, and possible assignments to a set of values for each object,
    determine a 1:1 mapping of objects to values that is compatible with the possible
    options.

    If no such mapping is possible, the returned dictionary is empty.

    Example
    -------
    >>> possible_mappings = {
        "a": [1, 2, 3],
        "b": [3],
        "c": [2, 3],
    }
    >>> match_to_unique_assigments(possible_mappings)
    {"a": 1, "b", 3, "c": 2}
    """
    if possible_mappings:
        pass
    mappings = {}
    for key, a_value in possible_mappings.items():
        mappings[key] = set(a_value)
    one_to_one = {}
    unassigned_values = set().union(*mappings.values())

    def value_can_be_assigned_to(value: Val, map: Dict[Obj, Set[Val]]) -> List[Obj]:
        """
        Return a list of objects that this value can be assigned to.
        """
        return [obj for obj, list_of_values in map.items() if value in list_of_values]

    def remove_value_from_all_mappings(value: Val, map: Dict[Obj, Set[Val]]) -> None:
        """
        Removes a value from all lists in mappings, if it is there.
        """
        for obj, list_of_values in map.items():
            if value in list_of_values:
                map[obj].remove(value)

    while len(one_to_one) < len(possible_mappings):
        # There is at least one object that does not have a value matched to it.
        obj_to_assign = None
        val_to_assign = None
        if any([len(value_list) == 0 for value_list in mappings.values()]):
            # There is at least one object that does not have anything it can be mapped to.
            # Return the failure case.
            return {}

        # If 1 value can only be assigned to a single object, make this assignment.
        for a_value in unassigned_values:
            possible_assignments = value_can_be_assigned_to(a_value, mappings)
            if len(possible_assignments) == 1:
                obj_to_assign = possible_assignments[0]
                val_to_assign = a_value
                break

        if obj_to_assign is None:
            # Previous loop failed to find any values that can only be mapped to
            # one object.

            # Instead, if any objects only have a single value they can take, we assign this now.
            for obj, set_of_values in mappings.items():
                if len(set_of_values) == 1:
                    obj_to_assign = obj
                    (val_to_assign,) = set_of_values
                    break
        if obj_to_assign is None:
            # Failed to find any objects that can only take one value.
            # Naively, our best approach now is to go through each object in sequence,
            # and arbitrarily assign it to one of its values.
            # Then, compute if a possible assignment solution still exists.
            # If it does, make this assignment, otherwise retry with a different arbitrary assignment.
            # If we exhaust all possible assignments in this way, there is no solution.
            still_a_possible_solution = None
            for obj in mappings.keys():
                obj_to_assign = obj

                for a_value in mappings[obj]:
                    val_to_assign = a_value

                    # Create a copy of mappings with this assignment having been made
                    mappings_copy = deepcopy(mappings)
                    remove_value_from_all_mappings(val_to_assign, mappings_copy)
                    mappings_copy.pop(obj_to_assign, None)

                    # Determine if a solution to the assignment remains
                    still_a_possible_solution = match_to_unique_assignments(mappings_copy)

                    if still_a_possible_solution:
                        break
                if still_a_possible_solution:
                    break
            if still_a_possible_solution:
                # We have actually computed the solution, which we obtain from combining our
                # existing one_to_one mappings with the solution we just received + our arbitrary
                # assignment.
                return {
                    obj_to_assign: val_to_assign,
                    **one_to_one,
                    **still_a_possible_solution,
                }
            else:
                return {}

        # Having determined the object to assign, make the assignment
        one_to_one[obj_to_assign] = val_to_assign
        remove_value_from_all_mappings(val_to_assign, mappings)
        mappings.pop(obj_to_assign, None)
    return one_to_one


def on_readonly_error(f: Callable[[Path], None], path: Path, exc_info) -> None:
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file) it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=on_readonly_error)``
    """
    os.chmod(path, stat.S_IWRITE)
    f(path)


def provide_tmp_directory(
    clean_on_error: bool = True,
    clean_on_success: bool = True,
    pass_dir_as_arg: Optional[str] = None,
    where: Optional[Path] = None,
) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
    """
    Wraps the execution of a function with the creation and optional teardown of a
    temporary directory, that can be optionally passed to the wrapped function.

    :param clean_on_error: If True, the temporary directory that is created will be removed if
    the wrapped function raises an error.
    :param clean_on_success: If True, the temporary directory that is created will be removed
    if the wrapped function returns without raising an error.
    :param pass_dir_as_arg: If provided, the wrapped function will automatically be passed a
    keyword argument whose name is the value of `pass_dir_as_arg`, and whose value is the path
    to the created temporary directory.
    :param where: If provided, this should be a path to a predefined location to use as the
    temporary directory. It must not currently exist on the filesystem, to ensure safety when
    deleting it.
    """

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        tmp_directory = None
        if where is not None:
            tmp_directory = where
            if tmp_directory.exists():
                raise RuntimeError(
                    f"Will not use existing location ({where}) as a temporary directory."
                )
            tmp_directory.mkdir()
        else:
            tmp_directory = mkdtemp()

        def _inner(*args, **kwargs) -> Any:
            return_val = None
            try:
                if pass_dir_as_arg:
                    return_val = func(*args, **kwargs, **{pass_dir_as_arg: tmp_directory})
                else:
                    return_val = func(*args, **kwargs)
            except Exception as e:
                if clean_on_error:
                    shutil.rmtree(tmp_directory, onerror=on_readonly_error)
                raise e
            if clean_on_success:
                shutil.rmtree(tmp_directory, onerror=on_readonly_error)
            return return_val

        return _inner

    return decorator
