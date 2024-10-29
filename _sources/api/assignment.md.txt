# The `Assignment` Class

The `Assignment` class represents an assignment specification as a Python object.
It mostly contains metadata about the assignment, and the heavy-lifting of comparing the assignment to an actual directory on the filesystem is delegated to the [`Directory` class](./directory.md).
The `Assignment` class is responsible for assembling the text output that is returned from the validation methods of the `Directory` class, however.

```{eval-rst}
.. currentmodule:: assignment_submission_checker.assignment

.. autoclass:: Assignment
    :members:
    :undoc-members:
```
