import shutil
import os
import pytest


@pytest.fixture
def create_temp_archive():
    def _create_temp_archive(root_dir, dir_path, extension, archive_name="archive"):
        cwd = os.getcwd()
        archive_path = f"{cwd}/{archive_name}"
        dir_name = dir_path.split("/")[-1]
        os.chdir(root_dir)
        shutil.make_archive(
            base_name=archive_path,
            format=extension,
            root_dir=root_dir,
            base_dir=dir_name,
        )
        os.chdir(cwd)
        if extension == "xztar":
            extension = "tar.xz"
        return f"archive.{extension}"

    return _create_temp_archive


@pytest.fixture
def data_inputs():
    return [
        "test.md",
        "test.css",
        "test.yaml",
        "test.sh",
        "test.tf",
        "test.py",
        "test.js",
        "Dockerfile",
        "test.html",
        "test.java",
        "test.ts",
    ]
