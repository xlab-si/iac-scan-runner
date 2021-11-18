from os import path
from shutil import unpack_archive
from subprocess import check_output, STDOUT, CalledProcessError
from tarfile import is_tarfile
from typing import Optional
from uuid import uuid4
from zipfile import is_zipfile

from iac_scan_runner.check_output import CheckOutput


def run_command(command: str, directory: str = ".") -> CheckOutput:
    """Run command with arguments in directory and return the output and return code

    :param command: A command to run
    :param directory: Target directory where the command will be executed (default is current dir)
    """
    try:
        return CheckOutput(check_output(command, cwd=directory, shell=True, stderr=STDOUT).decode('utf-8'), 0)
    except CalledProcessError as e:
        return CheckOutput(str(e.output.decode('utf-8')), e.returncode)


def determine_archive_format(archive_path: str) -> str:
    """Figures out the format of the supplied archive file
    
    :param archive_path: Path to the archive file
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
    """creates a unique random pathname and select last 6 characters

    :param prefix: Pathname prefix
    :param suffix: Pathname suffix
    """
    pathname = prefix + str(uuid4().hex)[-6:] + suffix
    if path.exists(pathname):
        return generate_random_pathname(prefix)
    else:
        return pathname


def unpack_archive_to_dir(archive_path: str, output_dir: Optional[str]) -> str:
    """Unpacks archive to a specified directory

    :param archive_path: Path to the archive file
    :param output_dir: Directory where IaC will be unpacked to
    """
    try:
        if not output_dir:
            output_dir = generate_random_pathname()

        iac_format = determine_archive_format(archive_path)
        unpack_archive(archive_path, output_dir, iac_format)
        return output_dir
    except Exception as e:
        raise Exception(f'Nonexistent check: {str(e)}')
