# Assignment Submission Checker

- [Assignment Submission Checker](#assignment-submission-checker)
  - [Overview](#overview)
    - [Disclaimer](#disclaimer)
  - [Current Configuration](#current-configuration)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Common configuration options](#common-configuration-options)
      - [`-h`, `--help`](#-h---help)
      - [`-i`, `--ignore-extra-files`](#-i---ignore-extra-files)
      - [`-v`, `--version`](#-v---version)
      - [`-c`, `--check-cnumber`](#-c---check-cnumber)
  - [Changelog](#changelog)

## Overview

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

### Disclaimer

The `assignment-checker` does *not* provide any reflection or indication of the grade you may receive for a submission you make.
It simply checks that the organisational structure of your submission matches that which is laid out in the assignment guidelines, so that you can be certain that your submission conforms to said specifications prior to making your submission.
Here, "assignment" refers to the marked submission made for the assignment listed under the [current configuration](#current-configuration).

Additionally, it cannot be used as evidence in the case of appeal against the grade awarded for an assignment.

## Current Configuration

The latest version of this package is configured to validate a submission for:

- COMP0233, academic year 2023/24, Assignment 1.

## Installation

Users should use `pip` to install this package.
This package will install dependencies that you might otherwise not have (nor want) in the environment in which you work on the assignment or classwork.
As such, we recommand that you first create a new virtual environment using either `conda` or `anaconda`, and then install this package.

When you make your environment, be sure to select Python 3.10 or later as the version of Python you want to install.

- [Creating a new environment with conda on the command line](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands).
- [Creating a new environment with the Anaconda GUI](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/#creating-a-new-environment)

Once you have created your environment, be sure to *activate* it before installing.
You can do this through your `GitBash` (Windows) or terminal (MacOS / Linux):

```bash
conda activate my_new_environment
```

To install the assignment checker into this environment, you can then run

```bash
python -m pip install git+https://github.com/UCL-COMP0233-23-24/assignment-submission-checker
```

The package will then place a command-line program, `assignment-checker`, into your environment.
You can run this program on the command line with the `-h` (`--help`) flag to see the usage pattern.

## Usage

```bash
assignment-checker [-h] [-v] [-i] [-c CHECK_CNUMBER] submission
```

The usual way to use the `assignment-checker` is in the following way:

```bash
assignment-checker path/to/my/submission.tar.gz
```

This will make the `assignment-checker` look for a file called `path/to/my/submission.tar.gz`, extract it, and then run the validation checks described in the [overview](#overview).
The result of this inspection will then be printed to the terminal for you to read.

### Common configuration options

#### `-h`, `--help`

Display the command line help for the `assignment-checker`.

#### `-i`, `--ignore-extra-files`

Ignore files that are present in the submission folder but which are not explicitly requested as part of the assignment.

Files such as data files for tests, or images for reports or READMEs, are not explicitly requested in the assignment specification but nonetheless should be included in your assignment.
However, the `assignment-checker` has no way of distinguishing files like this from genuinely unnecessary files in your submission, so you will often see files that you *need* as part of your assignment listed as "extra" files.
If you are confident that the only extra files that `assignment-checker` has found are those which you need as part of your submission, you can pass this flag to suppress the warning printout.
This should only be done if you are confident this is the case, and you do so at your own risk.

#### `-v`, `--version`

Display the current version of the package.
This information includes the current assignment that the program is configured to validate against.

#### `-c`, `--check-cnumber`

If you enter this option followed by your candidate number, the `assignment-checker` will also check that your candidate number matches the name of your submission folder.

```bash
$ assignment-checker -c 12345678 ./12345678.tar.gz
Candidate number 12345678 matches submission folder name.
$ assignment-checker -c 87654321 ./12345678.tar.gz
_________
! WARNING !
Submission name and candidate number do not match.
Submission is named 12345678 but your candidate number is 87654321.
---------------------
```

## Changelog

Previous versions of this package are listed below; along with the corresponding assignment they validated against, if this was different to the previous version.
