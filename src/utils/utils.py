"""
Senior Project : Hardware Encryption Device
Team 312
File : utils.py
Description: Functions that are used throughout the project.
"""

from pathlib import Path
import subprocess
from time import perf_counter
import re

REPO_NAME = "senior-design-312"


def run_shell_script(script_path, args=None):
    """
    Execute a shell script with optional arguments.

    Parameters
    ----------
    script_path : str
        The path to the shell script file.
    args : list, optional
        List of additional arguments to pass to the script.

    Returns
    -------
    CompletedProcess
        A subprocess.CompletedProcess instance.
    """
    command = ["/usr/bin/bash", script_path]
    if args:
        command.extend(args)

    try:
        result = subprocess.run(
            command, check=True, text=True, capture_output=True
        )
        return result
    except subprocess.SubprocessError as e:
        return f"Failed to execute shell script {script_path}: {e}"


def sleep_microseconds(us):
    end = perf_counter() + us / 1_000_000
    while perf_counter() < end:
        pass  # Busy-wait


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


def parse_log_line(line):
    """
    Extracts relevant information from a log line.
    Returns formatted log entry or None if the line doesn't match.
    """
    # Match GPIO-related logs
    gpio_match = re.search(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - (DEBUG) - .* \| (GPIO\d+)",
        line,
    )

    if gpio_match:
        timestamp, log_level, gpio = gpio_match.groups()
        time_part = timestamp.split(" ")[1]  # Extract time only
        formatted_time = time_part.replace(":", "").replace(
            ",", ""
        )  # Convert to `::timestamp` format
        # return f"::{formatted_time} | {log_level} | {gpio}"
        return f"{log_level} | {gpio}"

    # Match INFO logs
    info_match = re.search(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - (INFO) - (.*)",
        line,
    )

    if info_match:
        _, log_level, message = info_match.groups()
        return f"{log_level} | {message.strip()}"

    return None  # Ignore other log lines


if __name__ == "__main__":
    print(get_proj_root())
