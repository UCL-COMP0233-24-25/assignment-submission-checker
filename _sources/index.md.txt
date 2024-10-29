# Assignment Submission Checker

[assignment-specs-readme]: https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/blob/main/specs/README.md

```{toctree}
:maxdepth: 2

users
api
contributing
```

## About this Package

`assignment-submission-checker` provides the `assignment-checker` [command-line program](./users.md#usage), in the environment it is installed into.
It is intended to be used before you submit your work for UCL's COMP0233 module, and it will validate:

- Whether your repository / submission structure is as expected by the assignment specifications.
- Whether your git repository (and wider submission) is present and the repository root is in the correct location.
- Whether there are any files missing from your repository, that the assignment expects to be present.
- Whether you have included any files in your submission, that the assignment does not expect to be present.

Please note that in the case of files that are expected / unexpected, the `assignment-checker` strictly adheres to the assignment guidelines, and assumes you **intentionally** meant to include anything that it deems optional.
It will not flag data files that are in the correct folder, and have the correct data format, but that you don't actually use in your submission, for example.

The `assignment-checker` creates a copy / clone of the submission that you point it to, in your computer's temporary directory.
This ensures that any local copies of your repository are not affected by running the checker.

The `assignment-checker` reads the specifications it is checking against from a file, which it needs to fetch from the internet when it is run.
These files can be [viewed and downloaded][assignment-specs-readme] manually here, if you want to run the checker offline with the `-l` or `--local-specs` options.

```{attention}
**Disclaimer**

The `assignment-checker` command-line program does **not** provide any reflection or indication of the grade you may receive for a submission you make.
It only checks whether the organisational structure of your submission matches that which is laid out in the assignment guidelines, so that you can be certain that your submission conforms to said specifications prior to making your submission.

Additionally, it cannot be used as evidence in the case of appeal against the grade awarded for an assignment.
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
