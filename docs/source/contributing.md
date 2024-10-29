# Contributing

[current-specs-folder]: https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/tree/main/specs
[repo-issues]: https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/issues
[sphinx]: https://www.sphinx-doc.org/en/master/

```{contents} Contents
:depth: 2
```

## Adding an Assignment Configuration

The `specs` folder contains `.json` specifications that the `assignment-submission-checker` package requires when validating submissions.
To add an assignment specification, simply add a file to this folder using the [naming convention](#naming-convention) outlined below.
You can also [check the existing specifications][current-specs-folder] and use them as a template.

```{admonition} Do not delete this folder!
The `assignment-checker` needs to be able to fetch assignment specifications, and it expects to find them here.

If this folder is relocated, `assignment_submission_checker.cli:ASSIGNMENT_SPEC_REFERENCES` needs to be correspondingly updated too.
```

### Naming Convention

The naming convention for files in this folder should be

`YYYY-assignment_id`

where `YYYY` is the academic year the assignment is set in;

- `2024` would correspond to the `2024-2025` academic year, starting Sept 2024,
- `2025` would correspond to the `2025-2026` academic year, starting Sept 2025,

and `assignment_id` is the ID of the assignment itself;

- `001`, `002`, etc are used for assignments 1 and 2 (respectively),
- `LSA` is used for the late summer assessment.

### `json` Format

The keys that are recognised, and their effects, are detailed below;

- `git-marking-branch`: The branch within the submitted repository (if any) that will be used for marking. The repository will be switched to this branch to conduct validation.
- `git-alternative-branches`: A list of alternative branch names that will be used to search for the `git-marking-branch`, if a reference is not available that matches it. Typically this is used to allow `master` to be an alternative to `main`, for example.
- `number`: A number or sequence of characters used to identify the assignment within the module. Typically numeric, such as `001` or `002` for a course with multiple assignments, or `LSA` for the late summer assessment, for example.
- `title`: The assignment title.
- `year`: The academic year the assignment is set in.
- `structure`: The directory structure of the assignment. This is a further sequence of key-value pairs [that we outline below](#specifying-the-directory-structure).

#### Specifying the Directory Structure

The `structure` key should contain a further container with key-value pairs.
Keys that match the metadata keys below should be used to specify what the assignment checker should expect to find in this directory:

- `compulsory`: Defaults to an empty list if not provided. Values in this list should be files that are required to be part of the submission, and should be found in this directory.
- `data-patterns-key`: Defaults to an empty list if not provided. Values in this list should be file patterns that the checker can expect to find in this directory, and should treat as "optional" files (see below). This key is intended for directories where submissions are expected to contain custom data files or fixtures. Note that the checker does not confirm if these files are actually used in the submission.
- `git-root`: Defaults to `False` if not provided. If `True`, this directory should be the root of a git repository.
- `optional`: Defaults to an empty list if not provided. Values in this list should be files that are not required to be part of the submission, but should also not be considered "artefacts" or reported as "unexpected".
- `variable-name`: If provided, should be a shell match pattern. This informs the checker that this directory should have a variable name that matches the given pattern. Typically used when students are asked to include their candidate number or GitHub username in their submission. Note that the `structure` key itself will be interpreted as the name of the top-level directory in the submission, so this key typically appears there.

Any further keys that are found in this value are treated as further subdirectories, and their values should take the same form as described in this section.
This creates a nested structure of key-value entries, representative of the directory structure that the submission expects.

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

### Markdown vs RST

The documentation is written in Markdown and then uses `myst-parser` to translate this into `rst` format that Sphinx can interpret.
You can still use `rst` directives in Markdown files, and the `myst-parser` documentation contains a guide on how to do so:

- [To translate in-line directives.](https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html#roles-an-in-line-extension-point)
- [To translate block directives.](https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html#directives-a-block-level-extension-point)
