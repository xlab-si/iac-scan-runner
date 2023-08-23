import json
from datetime import datetime
from os import path
from shutil import unpack_archive
from subprocess import check_output, STDOUT, CalledProcessError
from tarfile import is_tarfile
from typing import Optional
from uuid import uuid4
from zipfile import is_zipfile

from bson import json_util

from iac_scan_runner.functionality.check_output import CheckOutput
import iac_scan_runner.vars as env


def run_command(command: str, directory: str = ".") -> CheckOutput:
    """
    Run command with arguments in directory and return the output and return code.

    :param command: A command to run
    :param directory: Target directory where the command will be executed (default is current dir)
    :return: CheckOutput object
    """
    try:
        return CheckOutput(check_output(command, cwd=directory, shell=True, stderr=STDOUT).decode("utf-8"), 0)
    except CalledProcessError as e:
        return CheckOutput(str(e.output.decode("utf-8")), e.returncode)


def determine_archive_format(archive_path: str) -> str:
    """
    Figure out the format of the supplied archive file.

    :param archive_path: Path to the archive file
    :return: String with archive format (zip or tar)
    """
    if is_zipfile(archive_path):
        return "zip"
    if is_tarfile(archive_path):
        return "tar"
    raise Exception(
        f"Unsupported archive format: '{archive_path}'. The packaging format should be one of: zip, tar.")


def generate_random_pathname(prefix: str = "", suffix: str = "") -> str:
    """
    Create a unique random pathname and select last 6 characters.

    :param prefix: Pathname prefix
    :param suffix: Pathname suffix
    :return: String with random pathname
    """
    pathname = prefix + str(uuid4().hex)[-6:] + suffix
    if path.exists(pathname):
        return generate_random_pathname(prefix)
    return pathname


def unpack_archive_to_dir(archive_path: str, output_dir: Optional[str]) -> str:
    """
    Unpack archive to a specified directory.

    :param archive_path: Path to the archive file
    :param output_dir: Directory where IaC will be unpacked to
    :return: String output dir name
    """
    try:
        if not output_dir:
            output_dir = generate_random_pathname()

        iac_format = determine_archive_format(archive_path)
        unpack_archive(archive_path, output_dir, iac_format)
        return output_dir
    except Exception as e:
        raise Exception(f"Nonexistent check: {str(e)}") from e


def write_string_to_file(check_name: str, dir_name: str, output_value: str) -> None:
    """
    Write string to given file inside specified directory.

    :param check_name: Name of the check
    :param dir_name: Directory name
    :param output_value: Content written to given file
    """
    file_name = dir_name + "/" + check_name + ".txt"
    try:
        with open(file_name, "w", encoding="utf-8") as text_file:
            text_file.write(output_value)
    except Exception as e:
        raise Exception(f"Error while writing string to file: {str(e)}.") from e


def write_html_to_file(file_name: str, output_value: str) -> None:
    """
    Write string to given file inside specified directory.

    :param file_name: File name
    :param output_value: Content written to given file
    """
    file_name = f"{env.ROOT_DIR}/outputs/generated_html/" + file_name + ".html"
    try:
        with open(file_name, "w", encoding="utf-8") as text_file:
            text_file.write(output_value)
    except Exception as e:
        raise Exception(f"Error storing HTML to file: {str(e)}.") from e


def file_to_string(file_path: str) -> str:
    """
    Read the file given by path and returns its contents as string output.

    :param file_path: Path of the file
    :return output: Content read from file in form of a string
    """
    output = ""
    try:
        with open(file_path, "r", encoding="utf-8") as text_file:
            output = str(text_file.read())
    except Exception as e:
        raise Exception(f"Error while reading file: {str(e)}.") from e
    return output


def parse_json(data):
    """
    Convert bson to dictionary.

    :param data: json
    :return: dictionary
    """
    try:
        parsed_data = json.loads(json_util.dumps(data))
    except Exception as e:
        print(f"Could not parse JSON, error: {e}")
    return parsed_data


def days_passed(time_stamp: str) -> int:
    """
    Calculate how many days have passed between today and given timestamp.

    :param time_stamp: Timestamp in format %m/%d/%Y, %H:%M:%S given as string
    :return: Integer which denotes the number of days passed
    """
    time1 = datetime.strptime(time_stamp, "%m/%d/%Y, %H:%M:%S")
    time2 = datetime.now()  # current date and time
    delta = time2 - time1
    string_delta = str(delta)

    if string_delta.find("days") > -1:
        days = string_delta.split(" ")
        return int(days[0])
    return 0
