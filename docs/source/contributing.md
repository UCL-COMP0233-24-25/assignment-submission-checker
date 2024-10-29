# Contributing

[repo-issues]: https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/issues
[sphinx]: https://www.sphinx-doc.org/en/master/

```{contents} Contents
:depth: 2
```

## Reporting a Bug

If you encounter a bug in the submission checker, please [open an issue][repo-issues].
In your bug report, please include steps to replicate the bug that you encountered, plus any other relevant information such as the assignment specs you were trying to check against.

## Contributing Code

If you would like to contribute to this tool, please fork this repository and open a pull request.
Once your pull request is ready, please tag `@UCL-COMP0233-24-25/comp0233-admin` for review, and a member of the team will review your pull request at their earliest convenience.
You can speed up the process by including a helpful title and description in your pull request, and linking to any relevant issues that your pull request addresses.

If you are planning to contribute code, you might also want to take a look at our [API Reference](./api.md) to familiarise yourself with the codebase.

## Building the Documentation

The documentation is built [using `Sphinx`][sphinx] and deployed via GitHub actions whenever a push to `main` occurs.
The documentation is also built for each PR branch against `main`, however these builds are not deployed.

To build the docs locally, ensure that you have both `sphinx` and `myst-parser` installed in your developer environment.
Alternatively, you can install this package with its developer (`dev`) optional requirements, which will fetch the two aforementioned packages.

Once you have installed the requirements, navigate to the repository root directory and run

```bash
(dev-environment) $ sphinx-build -M html docs/source docs/build
```

to build the documentation (in `html` format), with the output being placed into `docs/build`.
You can then view the documentation by opening the created `html` files inside a browser.