import os
import shutil
import tarfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from glob import glob
from pathlib import Path
from random import choices
from string import ascii_letters, digits
from typing import ClassVar, List, Literal, Tuple

import git


@dataclass
class Assignment:
    # A name that can be assigned to the assignment for printing purposes
    name: str
    # The path to the submission archive currently being examined.
    # This should be set with the set_target_archive method,
    # and it defaults to None.
    target_archive: ClassVar[Path] = None
    # The location of the root of the git repository that should have been submitted.
    # If None, no git repository is expected.
    git_root: Path = None

    # A name for the temporary directory in which the archive will be extracted,
    # then cleaned once checks are completed
    tmp_dir: ClassVar[Path]

    # Archive tool to use to extract the submission archive
    archive_tool: Literal["tar", "zip"] = "tar"
    # List of files that are expected to be present in the submission archive,
    # given as relative paths from the TOP LEVEL of the extracted archive.
    expected_files: List[str] = field(default_factory=lambda: [])

    @property
    def top_level_folder(self) -> str:
        """
        The name of the top-level folder that should appear after extracting the archive.
        """
        if self.target_archive is not None:
            return self.target_archive.stem.split(".")[0]  # .tar.gz has two suffixes
        else:
            return None

    def __post_init__(self) -> None:
        """
        Create a random string to use as the temporary directory for checking the submission status,
        once the __init__ method has set member variables.
        """
        self.tmp_dir = Path(
            datetime.utcnow().strftime("%Y%m%d%H%M%S")
            + "".join(choices(ascii_letters + digits, k=16))
        )
        self.git_root = Path(self.git_root)

        if self.archive_tool not in ["tar", "zip"]:
            raise ValueError(f"I don't recognise the compression tool {self.archive_tool}.")

        return

    def check_for_git_root(self) -> Tuple[bool, bool, str, str]:
        """
        Check that a git repository exists in the submission at the location provided.

        Return a tuple of three elements:
        1. A bool, whether the repository was found at the expected location. Note that if self.git_root is None, this always returns FALSE.
        2. A bool, whether the repository was clean after extraction.
        3. Any error message that was produced in attempting to find the repository (only non-empty if the repository was not present).
        4. A message about the untracked changes that were present in a dirty working tree.
        """
        repo_present = False
        repo_present_msg = ""
        repo_clean = False
        repo_clean_msg = ""
        if self.git_root is not None:
            # Attempt to find the repository
            try:
                repo = git.Repo(self.tmp_dir / f"{self.top_level_folder}" / self.git_root)
                repo_present = True
            except Exception as e:
                repo_present = False
                repo_present_msg = f"Expected to find a git repository at {self.top_level_folder / self.git_root} but encountered an error:\n\t{str(e)}"

            # If there is a repository, check the working tree is clean
            if repo_present:
                repo_clean = not repo.is_dirty(untracked_files=True)

                # Provide information about a dirty working tree if appropriate
                if not repo_clean:
                    if repo.untracked_files:
                        repo_clean_msg = f"You have untracked files in your git repository: {repo.untracked_files}"
                    else:
                        changed = [item.a_path for item in repo.index.diff(None)]
                        if changed:
                            repo_clean_msg = f"You have untracked changes to the following files in your git repository: {changed}"

        return repo_present, repo_clean, repo_present_msg, repo_clean_msg

    def extract_to_temp_dir(self) -> None:
        """
        Extract the submission folder into the temporary directory.

        Removes / cleans the temporary directory if it already exists for safety.
        """
        # If there is no current target archive set, raise error and halt
        if self.target_archive is None:
            raise ValueError(f"No target archive set, self.target_archive = {self.target_archive}.")

        # Clean temporary directory if it already exists
        self.purge_tmp_dir()

        # Create new temporary directory and extract submission folder into it
        os.mkdir(self.tmp_dir)

        # Attempt extraction
        try:
            if self.archive_tool == "tar":
                tarfile.open(self.target_archive).extractall(path=self.tmp_dir)
            elif self.archive_tool == "zip":
                zipfile.ZipFile(self.target_archive).extractall(path=self.tmp_dir)
        except Exception as e:
            raise RuntimeError(
                f"ERROR: Could not extract the file {self.target_archive} using {self.archive_tool}, encountered the following error:\n\t{str(e)}.\nMake sure you have compressed your assignment using the correct compression tool (tar/zip) and have provided the correct path to your submission file."
            )

        return

    def purge_tmp_dir(self) -> None:
        """
        Remove (if it exists) the temporary directory.
        """
        if os.path.exists(self.tmp_dir) and os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        return

    def search_for_missing_files(self) -> Tuple[List[str], List[str]]:
        """
        Search the extracted archive for the files which are expected to be present in the submission.

        Return two lists: the first of the files that were not found but expected, the second of files that were found but were not expected.
        """
        # Fetch all files present in the archive directory, excluding the .git repository
        archive_root_dir = self.tmp_dir / self.top_level_folder
        all_files_and_dirs = glob("**", root_dir=archive_root_dir, recursive=True)
        all_files_present = [
            file for file in all_files_and_dirs if not os.path.isdir(archive_root_dir / file)
        ]

        # Determine which files are expected, but not present
        # This is the (set) complement of the expected files against those that were found
        not_found = list(set(self.expected_files) - set(all_files_present))

        # Determine which files were found, but not expected
        not_expected = list(set(all_files_present) - set(self.expected_files))

        return sorted(not_found), sorted(not_expected)

    def set_target_archive(self, target: Path = None) -> None:
        """
        Set the self.target_archive member to the Path provided.

        Throw an error if the target Path does not exist, unless it is None.
        """
        if (target is None) or os.path.exists(target):
            self.target_archive = target
        else:
            raise FileNotFoundError(f"Could not locate an archive at {target}")

        return
