"""
Senior Project : Hardware Encryption Device
Team 312
File : utils.py
Description: Functions that are used throughout the project.
"""

from pathlib import Path

REPO_NAME = "senior-design-312"


def get_proj_root() -> Path:
    """
    Gets the project root.
    - Will get the full path of the repo regardless of OS or path.

    Returns:
    --------
    path : pathlib.Path
    """
    file_path = Path(__file__).resolve()  # Get the absolute path of the script

    # Find "senior-design-312" in the path and keep only up to that directory
    for parent in file_path.parents:
        if parent.name == REPO_NAME:
            project_root = parent
            break
    else:
        project_root = None  # If "senior-design-312" is not found

    return project_root


def ensure_path(path: str) -> None:
    """
    Ensures the given path exists.
    - If it's a directory, create all necessary parent folders.
    - If it's a file, create all parent folders and an empty file if it doesn't exist.

    :param path: The path (file or directory) to check and create.
    """
    path_obj = Path(path)

    if path_obj.suffix:  # Check if it's a file (has an extension)
        path_obj.parent.mkdir(
            parents=True, exist_ok=True
        )  # Create parent folders
        path_obj.touch(exist_ok=True)  # Create file if it doesn't exist
    else:  # It's a directory
        path_obj.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print(get_proj_root())
