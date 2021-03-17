import os
from typing import Optional
import subprocess
import re


TAG_VERSION = re.compile("^\\d+\\.\\d+(\\.\\d+)?$")


def is_master_branch(version: str) -> bool:
    return version == "master"


def find_parent_git_folder(start_path: str) -> str:
    """
    Finds the folder where the `.git` folder resides starting from the
    given folder.
    :return:
    """
    previous_path = path = os.path.abspath(start_path)

    while not os.path.isdir(os.path.join(path, ".git")):
        path = os.path.dirname(path)

        if previous_path == path:
            raise Exception(f"Unable to find a git folder in {start_path}")

        previous_path = path

    return path


def get_tag_version(version: str) -> Optional[str]:
    """
    Returns the version if it matches, else it returns None.
    """
    m = TAG_VERSION.match(version)

    if not m:
        return None

    return m.group(0)


def is_changed_repo(context) -> bool:
    """
    Checks if the current repository has changed files
    """

    changed_files: str = context.workspace.run_output("""
        git diff-index HEAD --
    """)

    return not not changed_files.strip()


def is_release(version: Optional[str] = None) -> bool:
    if version is None:
        version = read_current_version_using_version_manager()

    return get_tag_version(version) == version


def read_current_version_using_version_manager() -> str:
    return subprocess.check_output([
        "vm", "-t",
    ], encoding='utf-8').strip()

