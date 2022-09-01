from os import path
from shutil import unpack_archive
from subprocess import check_output, STDOUT, CalledProcessError
from tarfile import is_tarfile
from typing import Optional
from uuid import uuid4
from zipfile import is_zipfile

from iac_scan_runner.check_output import CheckOutput


def run_command(command: str, directory: str = ".") -> CheckOutput:
    """
    Run command with arguments in directory and return the output and return code
    :param command: A command to run
    :param directory: Target directory where the command will be executed (default is current dir)
    :return: CheckOutput object
    """
    try:
        return CheckOutput(check_output(command, cwd=directory, shell=True, stderr=STDOUT).decode('utf-8'), 0)
    except CalledProcessError as e:
        return CheckOutput(str(e.output.decode("utf-8")), e.returncode)


def determine_archive_format(archive_path: str) -> str:
    """
    Figures out the format of the supplied archive file
    :param archive_path: Path to the archive file
    :return: String with archive format (zip or tar)
    """
    if is_zipfile(archive_path):
        return "zip"
    elif is_tarfile(archive_path):
        return "tar"
    else:
        raise Exception(
            "Unsupported archive format: '{}'. The packaging format should be one of: zip, tar.".format(archive_path)
        )


def generate_random_pathname(prefix: str = "", suffix: str = "") -> str:
    """
    Creates a unique random pathname and select last 6 characters
    :param prefix: Pathname prefix
    :param suffix: Pathname suffix
    :return: String with random pathname
    """
    pathname = prefix + str(uuid4().hex)[-6:] + suffix
    if path.exists(pathname):
        return generate_random_pathname(prefix)
    else:
        return pathname


def unpack_archive_to_dir(archive_path: str, output_dir: Optional[str]) -> str:
    """
    Unpacks archive to a specified directory
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
        raise Exception(f"Nonexistent check: {str(e)}")


def write_string_to_file(check_name: str, dir_name: str, output_value: str):
    """
    Writes string to given file inside specified directory
    :param check_name: Name of the check
    :param output_dir: Directory where log will be stored
    :param output_value: Content written to given file
    """
    file_name = dir_name + "/" + check_name + ".txt"
    try:
        with open(file_name, "w") as text_file:
            text_file.write(output_value)
    except Exception as e:
        raise Exception(f"Error while writing string to file: {str(e)}.")    

def write_html_to_file(file_name: str, output_value: str):
    """
    Writes string to given file inside specified directory
    :param check_name: Name of the check
    :param output_dir: Directory where log will be stored
    :param output_value: Content written to given file
    """
    file_name = "../outputs/generated_html/" + file_name + ".html"
    try:    
        with open(file_name, "w") as text_file:
            text_file.write(output_value)
    except Exception as e:
        raise Exception(f"Error storing HTML to file: {str(e)}.")           


def file_to_string(file_path: str) -> str:
    """
    Reads the file given by path and returns its contents as string output
    :param file_path: Path of the file
    :return output: Content read from file in form of a string
    """
    output = ""
    try:
        with open(file_path, "r") as text_file:
            output = str(text_file.read())
    # TODO: Narrow exceptions for this one and similar functions        
    except Exception as e:
        raise Exception(f"Error while reading file: {str(e)}.")           
    return output        
