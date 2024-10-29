# User Guide

[assignment-specs-readme]: https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/blob/main/specs/README.md
[github-clone-feature-issue]: https://github.com/UCL-COMP0233-24-25/assignment-submission-checker/issues/3

## Installation

Users should use `pip` to install this package.

```{tip}
**Which Environment To Install Into?**

We recommend that you install this package into your `COMP0233` environment, and **not** into the same environment that you are working on your solution in.
This package will install external dependencies that may conflict with those your assignment's solution requires, or install packages that your assignment should not make use of.
If you are using the `COMP0233` environment to write your solution, consider making a separate environment for this package to be installed into.
```

This package will install dependencies that you might otherwise not have (nor want) in the environment in which you work on the assignment or classwork.
As such, we recommand that you first create a new virtual environment using either `conda` or `anaconda`, and then install this package.

When you make your environment, be sure to select Python 3.10 or later as the version of Python you want to install.

- [Creating a new environment with conda on the command line](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands).
- [Creating a new environment with the Anaconda GUI](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/#creating-a-new-environment)

Once you have created your environment, be sure to **activate** it before installing.
You can do this through your `GitBash` (Windows) or terminal (MacOS / Linux):

```bash
$ conda create -n assignment-checker-environment -y python=3.10
```

To install the assignment checker into this environment, you can then run

```bash
$ conda activate assignment-checker-environment
(assignment-checker-environment) $ python -m pip install git+https://github.com/UCL-COMP0233-24-25/assignment-submission-checker
```

The package will then place a command-line program, `assignment-checker`, into your environment.
You can run this program on the command line with the `-h` (`--help`) flag to see the usage pattern.

### Updating

If you want to update to the latest version of the `assignment-checker`, you can run the same install command as above.
However, you may want to uninstall the old version first, just to make sure `pip` knows to fetch the latest version.

Don't forget to run these in the same conda environment as you originally installed the assignment checker into!

```bash
# Uninstall the old version, if you have it installed
(assignment-checker-environment) $ python -m pip uninstall assignment-submission-checker
# Fetch the latest version from GitHub
(assignment-checker-environment) $ python -m pip install git+https://github.com/UCL-COMP0233-24-25/assignment-submission-checker
```

## Usage

Once the `assignment-checker` is installed, you can invoke it from the command-line:

```bash
(assignment-checker-environment) $ assignment-checker --help
usage: assignment-checker [-h] [-g] [-l] [-q] [-v] [-o OUTPUT_FILE] assignment submission
```

Make sure that you have the environment you installed the `assignment-checker` into activated, otherwise you will get a command not found error.

### Quick Start

The basic usage of the `assignment-checker` tool is to provide it with the specifications of the assignment you plan to submit (`assignment` argument), and a local copy of your submission (`submission` argument).

```bash
(assignment-checker-environment) $ assignment-checker YYYY-XXX path/to/my/comp0233/assignment-folder
```

`YYYY-XXX` should correspond to one of the assignment specifications [found here][assignment-specs-readme]. `path/to/my/comp0233/assignment-folder` should be the file path to your local copy of your repository / submission.

#### Local Specifications

Fetching the assignment specifications requires an internet connection.
If you will be without an internet connection for an extended period of time, you can download the assignment specifications from the [`specs` folder][assignment-specs-readme] in this repository, and store them on your computer.
You can then direct the `assignment-checker` directly to the copy of the specifications you have downloaded using the `-l` or `--local-specs` flags, and give the path to the downloaded specifications as the `assignment` argument.

```bash
(assignment-checker-environment) $ assignment-checker --l /path/to/local/specs/YYYY-XXX.json path/to/my/comp0233/assignment-folder
```

#### GitHub Submissions (Experimental)

**NOTE:** This feature is new this year and as such, highly experimental. If you make use of this feature, we'd be grateful if you [took a look at the issue][github-clone-feature-issue] tracking this feature.

If you have a working internet connection, you can ask the `assignment-checker` to fetch your submission directly from its GitHub repository.
Note that:

- The `assignment-checker` will use the current user's `git` config to access and clone the repository from GitHub. Since your assignment repository will be private, this means you will need to have your computer setup so that `git` knows it's you who is cloning or pushing!
  - You can run `ssh -T git@github.com` in a `bash` terminal to check if your terminal can connect to, and your account is authenticated with, GitHub.
- The `assignment-checker` will create a clone of the repository you point it to inside your computer's temporary directory (normally `/tmp`), so that it does not conflict with any other local copies of the repository you might be working on.
  - You do not need to worry about loosing any work you have saved locally.
  - You **should not** try to keep working on the cloned repo created by the `assignment-checker`. It is inside your computer's temporary directory and so will be lost when your computer shuts down!
- Using `-g` or `--github-clone` requires a working internet connection, even if you are also using the `-l` or `--local-specs` options.

If you use the `-g` or `--github-clone` options, you replace the `submission` argument value with the `https` or `ssh` clone link for your repository.
For this repository (for example), this would be `git@github.com:UCL-COMP0233-24-25/assignment-submission-checker.git`.

```bash
(assignment-checker-environment) $ assignment-checker -g 2024-001 git@github.com:repo-owner/repo-name.git     # Clone via SSH
(assignment-checker-environment) $ assignment-checker -g 2024-001 https://github.com/repo-owner/repo-name.git # Clone via HTTPS
```

### Output

The `assignment-checker` will print information to the terminal once it has finished running.
This information is broken down into three levels:

- `FATAL`: there was an issue with the submission or assignment specifications that prevented the `assignment-checker` from completing its analysis of the submission. This is usually caused by an incorrect file structure, or git root in the wrong place, but bugs with the `assignment-checker` program are also reported here.
- `WARNING`: the submission does not match the assignment specifications in some way, however the validation was able to continue beyond this step. Missing files or directories are reported here.
- `INFORMATION`: the `assignment-checker` reports anything that is not incorrect, but might not be expected, in this section. For example, you might have created a custom data file that you're including in your submission. If you have placed it into the correct data folder, the `assignment-checker` will report that it found this data file. Note that you will need to check if you actually **intended** to include this data file in your submission!

If one of the above levels has nothing to report, it is omitted from the output.

### Other Usage Options

The `assignment-checker` has additional command-line options that can be used to configure how it runs.
Additionally, the command-line workflow backend can be used programmatically from within Python, via `assignment_submission_checker.cli_main:main`.

- `-h`, `--help`: Displays the command-line help for the tool.
- `-q`, `--quiet`: Suppresses the text output of the tool to the terminal. Make sure you're using the `-o`, `--output-file` option in conjunction with this one!
- `-v`, `--version`: Displays the version of the tool that you currently have installed.
- `-o`, `--output-file`: If you are finding the text output too long, or want to save it for later, you can have the tool write the output to a text file. You should provide the name of the text file that you want to write immediately after this flag. Note that `assignment-checker -o out.txt <other args>` is equivalent to `assignment-checker <other-args> >> out.txt`.
