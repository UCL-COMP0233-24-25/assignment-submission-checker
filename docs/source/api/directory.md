# The Directory Class

The `Directory` class allows us to compare a directory on the filesystem to a representation of a directory structure that we expect to be present.
A `Directory` instance stores a list of further `Directory` instances that implicitly encode its subdirectories - this results in the majority of class methods invoking some form of recursion to check compatibility or equality (amongst other things).

`Directory`s also contain metadata from the assignment specifications about which files (or types of files) they should contain, whether they should be the root of a git repository, and whether their name can be variable.
A top-level `Directory` is typically identified when the `parent` attribute is `None`; the `Assignment.structure` property of [the `Assignment` class](./assignment.md) typically makes such a `Directory` instance.

```{eval-rst}
.. currentmodule:: assignment_submission_checker.directory

.. autoclass:: Directory
    :members:
    :undoc-members:
```
