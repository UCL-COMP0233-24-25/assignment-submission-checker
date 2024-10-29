# Command-Line Interface

## Entry Function

The command-line interface `assignment-checker` directs to the `cli:cli` method;

```{eval-rst}
.. autofunction:: assignment_submission_checker.cli.cli
```

which serves to parse the command-line arguments and pass the corresponding Python values to the [backend function](#backend-function).

The `CLIParser` class is defined to have the command-line interface automatically display the help message when the user inputs invalid arguments.

```{eval-rst}
.. autoclass:: assignment_submission_checker.cli.CLIParser
    :members:
```

## Backend Function

The `cli_main` module contains the function that actually runs the validation workflow of the `assignment-checker`, `main`:

```{eval-rst}
.. autofunction:: assignment_submission_checker.cli_main.main
```

This function is deliberately separated from the command-line interface [entry function](#entry-function) to allow the validation workflow to be run from within Python scripts and workflows directly, without the need to open a subprocess and delegate to the shell.

The only other function in this module is the `fetch_spec` function, which handles fetching [assignment specifications](../contributing.md#adding-an-assignment-configuration) from the GitHub repository.

```{eval-rst}
.. autofunction:: assignment_submission_checker.cli_main.fetch_spec
```
