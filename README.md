# Assignment Submission Checker

This package is intended as a supplement to UCL teaching courses run by the [Advanced Research Computing (ARC) centre](https://www.ucl.ac.uk/advanced-research-computing/advanced-research-computing-centre).
Students on ARC courses that require electronic / online submission can utilise this package to check (on their local machine) that the archive they are submitting is of the correct format.

The package installs a command-line executable, `assignment-checker`, into the user's environment (the package `assignment-submission-checker` is also installed into the environment but is not intended for use as a Python API).
This command can be directed to a file on the user's local machine which they intend to submit for an graded assignment, and will run a series of validation checks on the structure, contents, and names used in the submission.

Specifically, the program will check that:

- The name of the file being submitted is a valid candidate number. Passing the `-c` (`--check-cnumber`) flag along with your 8-digit candidate number will validate that the file name matches your candidate number.
- The submission contains a git repository at the expected location.
- The submission's git repository (if present) is clean.
- The submission contains all expected files, and these are located in the correct folders.
- The submission does not contain any files that are not explicitly specified as part of the submission. Note that additional data files written by students, or images that need to be included as part of a report file (if requested) will also be flagged by this check. It can be disabled (at the user's risk) by passing the `-i`, (`--ignore-extra-files`) flag.

## Currently Configuration

The package is currently configured to validate a submission for:

- COMP0233, academic year 2023/24, Assignment 1.

## Installation

Users should use `pip` to install this package.

## Usage

## Changelog

Previous versions of this package are listed below; along with the corresponding assignment they validated against, if this was different to the previous version.
