# THIS TOOL IS CURRENTLY BEING REDEVELOPED, AND AS SUCH THE API DESCRIBED BELOW IS NOT FULLY IMPLEMENTED

Please check back here next week for updates.

# Assignment Submission Checker

- [THIS TOOL IS CURRENTLY BEING REDEVELOPED, AND AS SUCH THE API DESCRIBED BELOW IS NOT FULLY IMPLEMENTED](#this-tool-is-currently-being-redeveloped-and-as-such-the-api-described-below-is-not-fully-implemented)
- [Assignment Submission Checker](#assignment-submission-checker)
  - [Overview](#overview)
  - [Disclaimer](#disclaimer)
    - [MacOS AppleDouble files](#macos-appledouble-files)
  - [Installation](#installation)
    - [Updating](#updating)
  - [Usage](#usage)

## Overview

## Disclaimer

The `assignment-checker` does *not* provide any reflection or indication of the grade you may receive for a submission you make.
It simply checks that the organisational structure of your submission matches that which is laid out in the assignment guidelines, so that you can be certain that your submission conforms to said specifications prior to making your submission.
Here, "assignment" refers to the marked submission made for the assignment listed under the [current configuration](#current-configuration).

Additionally, it cannot be used as evidence in the case of appeal against the grade awarded for an assignment.

### MacOS AppleDouble files

TSTK convert this to an issue so it can persist outside the README.

If you are running MacOS; you may encounter an issue where certain metadata files and folders are created when compressing or extracting your archive.
These typically come with names like `._DS_store`, `_MACOSX`, or `._<name_of_an_actual_file_in_your_submission>`.
The assignment checker will detect such files when it attempts to extract your submission, and will flag them accordingly.

If you are creating your archive via `tar`, a possible workaround to avoid creation of these files is to pass the `--disable-copyfile`;

```bash
tar --disable-copyfile <usual_arguments_for_compressing>
```

If you cannot prevent the pollution of your archive with these files;

- Clone your repository onto a UCL machine (or use remote desktop) to get access to a Windows machine, and create the archive on there.
- If you are working on a group project, consider asking a member of your group who is using Windows or Linux to make the submission folder instead.

If the above does not work, it is likely that the additional files are being created when your submission is being *extracted* rather than when they are being *compressed*.
In this case, the assignment checker has some built-in robustness, but it cannot catch every case.
You might consider using the `--ignore-extra-files` flag if you are confident that the only unexpected files are those such as this.

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

### Updating

If you want to update to the latest version of the `assignment-checker`, you can run the same install command as above.
However, you may want to uninstall the old version first, just to make sure `pip` knows to fetch the latest version.
Don't forget to run these in the same conda environment as you originally installed the assignment checker into!

```bash
python -m pip uninstall assignment-submission-checker                                           # Uninstall the old version, if you have it installed
python -m pip install git+https://github.com/UCL-COMP0233-23-24/assignment-submission-checker   # Fetch the latest version from GitHub
```

## Usage
