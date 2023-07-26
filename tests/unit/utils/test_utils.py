import os
from shutil import rmtree
from zipfile import ZipFile
from tarfile import open as tar_open
from datetime import datetime

import pytest
from iac_scan_runner import utils
import iac_scan_runner.vars as env


class TestUtils:
    # pylint: disable=no-self-use,pointless-statement,unused-variable

    def test_run_command_default_dir(self):
        if os.path.exists("tempdir"):
            rmtree("tempdir", True)
        os.mkdir("tempdir")
        os.chdir("tempdir")
        with open("file1", "w", encoding="utf-8") as f:
            None
        with open("file2", "w", encoding="utf-8") as f:
            None
        with open("file3", "w", encoding="utf-8") as f:
            None
        output = utils.run_command("ls")
        assert output.output == "file1\nfile2\nfile3\n"
        assert output.rc == 0
        os.chdir("..")
        rmtree("tempdir", True)

    def test_run_command_dir(self):
        if not os.path.exists("tempdir"):
            rmtree("tempdir", True)
        os.mkdir("tempdir")
        with open("tempdir/file1", "w", encoding="utf-8") as f:
            None
        with open("tempdir/file2", "w", encoding="utf-8") as f:
            None
        with open("tempdir/file3", "w", encoding="utf-8") as f:
            None
        output = utils.run_command("ls", "tempdir")
        assert output.output == "file1\nfile2\nfile3\n"
        assert output.rc == 0
        rmtree("tempdir", True)

    def test_run_command_nonexistentdir(self):
        if not os.path.exists("tempdir"):
            rmtree("tempdir", True)
        os.mkdir("tempdir")
        with open("tempdir/file1", "w", encoding="utf-8") as f:
            None
        with open("tempdir/file2", "w", encoding="utf-8") as f:
            None
        with open("tempdir/file3", "w", encoding="utf-8") as f:
            None
        output = utils.run_command("grep 'non-exeistent word'", "tempdir")
        assert output.output == ""
        assert output.rc == 1
        rmtree("tempdir", True)

    def test_determine_archive_format_zip(self):
        if os.path.exists("archive.zip"):
            os.remove("archive.zip")

        with open("archive.zip", "w", encoding="utf-8") as f:
            None
        with ZipFile("archive.zip", "w") as f:
            None
        file_format = utils.determine_archive_format("archive.zip")
        assert file_format == "zip"
        os.remove("archive.zip")

    def test_determine_archive_format_tar(self):
        if os.path.exists("arvhie.tar"):
            os.remove("archive.tar")

        with tar_open("archive.tar", "w", encoding="utf-8") as f:
            None
        file_format = utils.determine_archive_format("archive.tar")
        assert file_format == "tar"
        os.remove("archive.tar")

    def test_determine_archive_format_txt(self):
        if os.path.exists("archive.txt"):
            os.remove("archive.txt")

        with open("archive.txt", "w", encoding="utf-8") as f:
            None
        with pytest.raises(Exception) as e:
            utils.determine_archive_format("archive.txt")
        assert (
            str(e.value) == "Unsupported archive format: "
            "'archive.txt'. The packaging format should be one of: zip, tar."
        )
        os.remove("archive.txt")

    def test_generate_random_pathname_new_name(self, mocker):
        mock_uuid4 = mocker.patch("iac_scan_runner.utils.uuid4")
        mock_uuid4.return_value.hex = "_"
        pathname = utils.generate_random_pathname("file", "name")
        assert pathname == "file_name"

    def test_generate_random_pathname_existing_name(self, mocker):
        if os.path.exists("file_name"):
            os.remove("file_name")

        mock_uuid4 = mocker.patch("iac_scan_runner.utils.uuid4")
        mock_uuid4.return_value.hex = "_"
        with open("file_name", "w", encoding="utf-8") as f:
            None
        pathname = utils.generate_random_pathname("file", "name")
        assert pathname == "file_"
        os.remove("file_name")

    def test_unpack_archive_to_dir_random_dir(
        self, mocker, create_temp_archive, data_inputs
    ):
        if os.path.exists("archive.zip"):
            os.remove("archive.zip")

        if os.path.exists("tempdir"):
            rmtree("tempdir", True)
        os.mkdir("tempdir")
        mock_pathname = mocker.patch("iac_scan_runner.utils.generate_random_pathname")
        mock_pathname.return_value = "tempdir"

        mock_format = mocker.patch("iac_scan_runner.utils.determine_archive_format")
        mock_format.return_value = "zip"
        archive_root_dir = os.getcwd() + "/tests/data"
        dir_path = archive_root_dir + "/inputs"
        temp_zip = create_temp_archive(archive_root_dir, dir_path, "zip")

        utils.unpack_archive_to_dir(temp_zip, None)
        assert os.path.exists("tempdir")
        for i in os.listdir("tempdir/inputs"):
            assert i in data_inputs

        rmtree("tempdir", True)
        os.remove("archive.zip")

    def test_unpack_archive_to_dir_tempdir(
        self, mocker, create_temp_archive, data_inputs
    ):
        if os.path.exists("archive.zip"):
            os.remove("archive.zip")
        if os.path.exists("tempdir"):
            rmtree("tempdir", True)

        mock_format = mocker.patch("iac_scan_runner.utils.determine_archive_format")
        mock_format.return_value = "zip"
        archive_root_dir = f"{env.ROOT_DIR}/tests/data/inputs"
        dir_path = f"{env.ROOT_DIR}/tests/data/inputs/"
        temp_zip = create_temp_archive(archive_root_dir, dir_path, "zip")

        utils.unpack_archive_to_dir(temp_zip, "tempdir")
        assert os.path.exists("tempdir")
        for i in os.listdir("tempdir"):
            assert i in data_inputs

        rmtree("tempdir", True)
        os.remove("archive.zip")

    def test_unpack_archive_to_dir_nonexistent_archive(
        self, mocker
    ):
        mock_pathname = mocker.patch("iac_scan_runner.utils.generate_random_pathname")
        mock_pathname.return_value = "tempdir"

        mock_format = mocker.patch("iac_scan_runner.utils.determine_archive_format")
        mock_format.return_value = "zip"

        with pytest.raises(Exception) as e:
            utils.unpack_archive_to_dir("archive.zip", None)
        assert str(e.value) == "Nonexistent check: archive.zip is not a zip file"

    def test_write_string_to_file(self):
        if os.path.exists("tempdir"):
            rmtree("tempdir")

        os.mkdir("tempdir")
        _output_value = "Output value"
        _check_name = "mock_check"
        utils.write_string_to_file(
            check_name=_check_name, output_value=_output_value, dir_name="tempdir"
        )
        assert os.path.isfile("tempdir/mock_check.txt")
        with open("tempdir/mock_check.txt", "r", encoding="utf-8") as f:
            content = f.read()
        assert content == _output_value

        rmtree("tempdir", True)

    def test_write_string_to_file_no_dir(self):
        _output_value = "Output value"
        _check_name = "mock_check"
        with pytest.raises(Exception) as e:
            utils.write_string_to_file(
                check_name=_check_name, output_value=_output_value, dir_name="tempdir"
            )
        assert (
            str(e.value) == "Error while writing string to file: "
            "[Errno 2] No such file or directory: 'tempdir/mock_check.txt'."
        )

    def test_write_html_to_file(self):
        _output_value = "Output value"
        _file_name = "mock_check"
        if os.path.exists("outputs/generated_html/mock_check.html"):
            os.remove("outputs/generated_html/mock_check.html")
        utils.write_html_to_file(output_value=_output_value, file_name=_file_name)
        assert os.path.isfile(f"{env.ROOT_DIR}/outputs/generated_html/mock_check.html")
        with open(f"{env.ROOT_DIR}/outputs/generated_html/mock_check.html", "r", encoding="utf-8") as f:
            content = f.read()
        assert content == _output_value
        os.remove(f"{env.ROOT_DIR}/outputs/generated_html/mock_check.html")

    def test_write_html_to_file_bad_output(self):
        _output_value = b"Bytes!"
        _file_name = "mock_check"
        if os.path.exists("outputs/generated_html/mock_check.html"):
            os.remove("outputs/generated_html/mock_check.html")
        with pytest.raises(Exception) as e:
            utils.write_html_to_file(output_value=_output_value, file_name=_file_name)
        assert (
            str(e.value) == "Error storing HTML to file: write() argument must be str, not bytes."
        )
        os.remove(f"{env.ROOT_DIR}/outputs/generated_html/mock_check.html")

    def test_file_to_string(self):
        if os.path.exists("test_file"):
            os.remove("test_file")

        with open("test_file", "w", encoding="utf-8") as f:
            f.write("content")
        output = utils.file_to_string("test_file")
        assert output == "content"
        os.remove("test_file")

    def test_file_to_string_no_file(self):
        with pytest.raises(Exception) as e:
            utils.file_to_string("test_file")
        assert (
            str(e.value) == "Error while reading file: [Errno 2] No such file or directory: 'test_file'."
        )

    def test_file_to_string_bad_encoding(self):
        with open("test_file", "w", encoding="iso-8859-15") as f:
            f.write("€")
        with pytest.raises(Exception) as e:
            utils.file_to_string("test_file")
        assert (
            str(e.value) == "Error while reading file: "
            "'utf-8' codec can't decode byte 0xa4 in position 0: invalid start byte."
        )
        os.remove("test_file")

    def test_parse_json_json_data(self):
        data = "{'json': 'example'}"
        parsed_data = utils.parse_json(data)
        assert parsed_data == data

    def test_parse_json_bson_data(self):
        data = b"\x16\x00\x00\x00\x02hello\x00\x06\x00\x00\x00world\x00\x00"
        parsed_data = utils.parse_json(data)
        assert parsed_data == {
            "$binary": {"base64": "FgAAAAJoZWxsbwAGAAAAd29ybGQAAA==", "subType": "00"}
        }

    def test_days_passed(self, mocker):
        # Can only mock everything or nothing as datetime is immutable
        mock_now = mocker.patch("iac_scan_runner.utils.datetime")
        mock_now.now.return_value = datetime.strptime(
            "2/2/1991, 11:10:01", "%m/%d/%Y, %H:%M:%S"
        )
        time_stamp = "1/1/1990, 00:00:00"
        mock_now.strptime.return_value = datetime.strptime(
            time_stamp, "%m/%d/%Y, %H:%M:%S"
        )
        days = utils.days_passed(time_stamp)

        assert days == 397

    def test_days_passed_bad_input(self, mocker):
        # Can only mock everything or nothing as datetime is immutable
        mock_now = mocker.patch("iac_scan_runner.utils.datetime")
        mock_now.now.return_value = datetime.strptime(
            "1/1/1990, 11:10:01", "%m/%d/%Y, %H:%M:%S"
        )
        time_stamp = "1/1/1990, 10:10:10"
        mock_now.strptime.return_value = datetime.strptime(
            time_stamp, "%m/%d/%Y, %H:%M:%S"
        )
        days = utils.days_passed(time_stamp)

        assert days == 0
