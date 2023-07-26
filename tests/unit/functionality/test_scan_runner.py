import pytest
import os
import json
import iac_scan_runner.vars as env

from shutil import rmtree, copytree
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.functionality.scan_runner import ScanRunner


class TestScanRunner:
    # pylint: disable=no-self-use

    def test_init_iac_dir(self, mocker, data_zip_read, create_mock_UploadFile):
        start_len = len(os.listdir())

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = data_zip_read

        mock_IaC = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "data.zip",
                "content_type": "application/zip",
            }
        )

        ScanRunner._init_iac_dir(ScanRunner, mock_IaC)
        dir_name = ScanRunner.iac_dir

        end_len = len(os.listdir())

        assert end_len == start_len + 1

        rmtree(dir_name, True)
        ScanRunner.iac_dir = ""

    def test_init_iac_dir_no_spooled_file(self, create_mock_UploadFile):
        mock_IaC = create_mock_UploadFile(
            {
                "file": None,
                "filename": "exception_test_data.zip",
                "content_type": "application/zip",
            }
        )
        with pytest.raises(Exception):
            mock_IaC.file = None
            ScanRunner._init_iac_dir(ScanRunner, mock_IaC)

        iac_filename_local = list(
            filter(lambda x: x.startswith("exception_test_data.zip"), os.listdir())
        )[0]
        os.remove(iac_filename_local)

    def test_init_iac_dir_no_iac_file(self):
        with pytest.raises(Exception):
            ScanRunner._init_iac_dir(ScanRunner, None)

    def test_init_iac_dir_invalid_filename(
        self, mocker, data_zip_read, create_mock_UploadFile
    ):
        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = data_zip_read
        mock_IaC = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": 123,
                "content_type": "application/zip",
            }
        )
        with pytest.raises(Exception):
            ScanRunner._init_iac_dir(ScanRunner, mock_IaC)

    def test_clear_iac_dir(self, mocker):
        mock_ScanRunner = mocker.MagicMock(spec=ScanRunner)
        mock_ScanRunner.iac_dir = "test_iac_dir"
        if not os.path.exists("test_iac_dir"):
            os.mkdir("test_iac_dir")

        start = len(os.listdir())

        ScanRunner._cleanup_iac_dir(mock_ScanRunner)

        end = len(os.listdir())

        assert start == end + 1

    def test_run_checks_no_project_id(
        self,
        mocker,
        create_mock_ScanRunner,
        transform_htmlhint,
        htmlhint_response,
        htmlhint_json_response,
        clear_outputs,
    ):
        check_output = CheckOutput(htmlhint_response, 0)
        mock_ScanRunner = create_mock_ScanRunner()

        if not os.path.exists("run_checks_test_data"):
            copytree("tests/data/inputs", "run_checks_test_data")

        htmlhint = mocker.MagicMock()
        htmlhint.name = "htmlhint"
        htmlhint.run.return_value = check_output

        mock_ScanRunner.iac_checks = {htmlhint.name: htmlhint}

        old = (
            len(os.listdir("outputs/generated_html")),
            len(os.listdir("outputs/json_dumps")),
            len(os.listdir("outputs/logs")),
        )

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        output = ScanRunner._run_checks(mock_ScanRunner, ["htmlhint"], "", "json")

        rmtree("run_checks_test_data", True)

        new = (
            len(os.listdir("outputs/generated_html")),
            len(os.listdir("outputs/json_dumps")),
            len(os.listdir("outputs/logs")),
        )

        assert transform_htmlhint(output["htmlhint"]) == transform_htmlhint(
            htmlhint_json_response["htmlhint"]
        )
        for i in range(len(old)):
            assert old[i] + 1 == new[i]

        clear_outputs(generated_html, json_dumps, logs)

    def test_run_checks_override_project_id(
        self,
        mocker,
        create_mock_ScanRunner,
        htmlhint_response,
        htmlhint_json_response,
        transform_htmlhint,
        clear_outputs,
    ):
        check_output = CheckOutput(htmlhint_response, 0)
        mock_ScanRunner = create_mock_ScanRunner()
        if not os.path.exists("run_checks_test_data"):
            copytree("tests/data", "run_checks_test_data")

        htmlhint = mocker.MagicMock()
        htmlhint.name = "htmlhint"
        htmlhint.run.return_value = check_output

        mock_ScanRunner.iac_checks = {htmlhint.name: htmlhint}

        old = (
            len(os.listdir("outputs/generated_html")),
            len(os.listdir("outputs/json_dumps")),
            len(os.listdir("outputs/logs")),
        )

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        output = ScanRunner._run_checks(
            mock_ScanRunner, ["htmlhint"], "invalid_project_id", "json"
        )

        rmtree("run_checks_test_data", True)

        new = (
            len(os.listdir("outputs/generated_html")),
            len(os.listdir("outputs/json_dumps")),
            len(os.listdir("outputs/logs")),
        )

        assert transform_htmlhint(output["htmlhint"]) == transform_htmlhint(
            htmlhint_json_response["htmlhint"]
        )
        for i in range(len(old)):
            assert old[i] + 1 == new[i]

        clear_outputs(generated_html, json_dumps, logs)

    def test_run_checks_valid_project_id(
        self,
        mocker,
        create_mock_ScanRunner,
        htmlhint_response,
        htmlhint_json_response,
        transform_htmlhint,
        load_project_return,
        clear_outputs,
    ):
        check_output = CheckOutput(htmlhint_response, 0)
        mock_ScanRunner = create_mock_ScanRunner()

        htmlhint = mocker.MagicMock()
        htmlhint.name = "htmlhint"
        htmlhint.run.return_value = check_output

        mock_ScanRunner.iac_checks = {htmlhint.name: htmlhint}

        old = (
            len(os.listdir("outputs/generated_html")),
            len(os.listdir("outputs/json_dumps")),
            len(os.listdir("outputs/logs")),
        )

        mock_ScanRunner.project_checklist = load_project_return(["htmlhint"])[
            "checklist"
        ]

        if not os.path.exists("run_checks_test_data"):
            copytree("tests/data", "run_checks_test_data")

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        output = ScanRunner._run_checks(
            mock_ScanRunner, [], "invalid_project_id", "json"
        )

        rmtree("run_checks_test_data", True)

        new = (
            len(os.listdir("outputs/generated_html")),
            len(os.listdir("outputs/json_dumps")),
            len(os.listdir("outputs/logs")),
        )

        assert transform_htmlhint(output["htmlhint"]) == transform_htmlhint(
            htmlhint_json_response["htmlhint"]
        )
        for i in range(len(old)):
            assert old[i] + 1 == new[i]

        clear_outputs(generated_html, json_dumps, logs)

    def test_run_checks_invalid_project_id(self, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        # Hardcode the Exception that set_scan_checklist would raise
        # when given an invalid project_id

        mock_ScanRunner.set_scan_checklist.side_effect = Exception(
            "Project id does not exist"
        )

        if not os.path.exists("run_checks_test_data"):
            copytree("tests/data", "run_checks_test_data")

        with pytest.raises(Exception) as e:
            ScanRunner._run_checks(mock_ScanRunner, [], "invalid_project_id", "json")

        assert str(e.value) == "Project id does not exist"

        rmtree("run_checks_test_data", True)

    def test_run_checks_invalid_checks(self, create_mock_ScanRunner, clear_outputs):
        mock_ScanRunner = create_mock_ScanRunner()
        if not os.path.exists("run_checks_test_data"):
            copytree("tests/data", "run_checks_test_data")

        mock_ScanRunner.iac_checks = {}

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        output = ScanRunner._run_checks(mock_ScanRunner, [123], "", "json")

        clear_outputs(generated_html, json_dumps, logs)

        rmtree("run_checks_test_data", True)

        assert list(output.keys()) == [
            "uuid",
            "archive",
            "time",
            "execution-duration",
            "verdict",
        ]
        assert output["verdict"] == "Passed"

    def test_enable_check(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        output = ScanRunner.enable_check(mock_ScanRunner, "mock_check", "")

        assert (
            output == f"Check: {mock_check.name} is now enabled and available to use."
        )

    def test_enable_check_already_enabled(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True  # Check will already be enabled

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        with pytest.raises(Exception) as e:
            ScanRunner.enable_check(mock_ScanRunner, "mock_check", "")

        assert str(e.value) == f"Check: {mock_check.name} is already enabled."

    def test_enable_check_nonexistent_check(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False

        mock_ScanRunner.iac_checks = {}

        with pytest.raises(Exception) as e:
            ScanRunner.enable_check(mock_ScanRunner, "mock_check", "")

        assert str(e.value) == f"Nonexistent check: {mock_check.name}"

    def test_enable_check_project_id(
        self, mocker, create_mock_ScanRunner, load_project_return, mock_add_check
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"
        mock_check_A.enabled = False

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"
        mock_check_B.enabled = True

        with open("mock_DB", "w") as f:
            json.dump(load_project_return([mock_check_B.name]), f)

        mock_ScanRunner.scan_project.add_check = mock_add_check
        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }

        output = ScanRunner.enable_check(
            mock_ScanRunner, mock_check_A.name, "valid_project_id"
        )

        with open("mock_DB", "r") as f:
            project = json.load(f)
        os.remove("mock_DB")

        assert mock_check_A.name in project["checklist"]
        assert (
            output == f"Check: {mock_check_A.name} is now enabled and available to use."
        )

    def test_disable_check_invalid_project_id(
        self, mocker, create_mock_ScanRunner, mock_add_check
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"
        mock_check_A.enabled = True

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"
        mock_check_B.enabled = True

        mock_ScanRunner.scan_project.add_check = mock_add_check
        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }

        with pytest.raises(Exception) as e:
            ScanRunner.enable_check(
                mock_ScanRunner, mock_check_A.name, "invalid_project_id"
            )

        assert str(e.value) == "Project id does not exist"

    def test_enable_check_project_id_nonexistent_check(
        self, mocker, create_mock_ScanRunner
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False

        mock_ScanRunner.iac_checks = {}
        mock_ScanRunner.persistence_enabled = True

        with pytest.raises(Exception) as e:
            ScanRunner.enable_check(mock_ScanRunner, "mock_check", "valid_project_id")

        assert str(e.value) == f"Nonexistent check: {mock_check.name}"

    def test_disable_check(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        output = ScanRunner.disable_check(mock_ScanRunner, "mock_check", "")

        assert output == f"Check: {mock_check.name} is now disabled and cannot be used."

    def test_enable_check_already_disabled(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False  # Check will already be disabled

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        with pytest.raises(Exception) as e:
            ScanRunner.disable_check(mock_ScanRunner, "mock_check", "")

        assert str(e.value) == f"Check: {mock_check.name} is already disabled."

    def test_disable_check_nonexistent_check(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True

        mock_ScanRunner.iac_checks = {}

        with pytest.raises(Exception) as e:
            ScanRunner.disable_check(mock_ScanRunner, "mock_check", "")

        assert str(e.value) == f"Nonexistent check: {mock_check.name}"

    def test_disable_check_project_id(
        self, mocker, create_mock_ScanRunner, load_project_return, mock_remove_check
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"
        mock_check_A.enabled = True

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"
        mock_check_B.enabled = True

        with open("mock_DB", "w") as f:
            f.write(
                json.dumps(load_project_return([mock_check_A.name, mock_check_B.name]))
            )

        mock_ScanRunner.scan_project.remove_check = mock_remove_check
        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }

        output = ScanRunner.disable_check(
            mock_ScanRunner, mock_check_A.name, "valid_project_id"
        )

        with open("mock_DB", "r") as f:
            project = json.loads(f.read())
        os.remove("mock_DB")

        assert mock_check_A.name not in project["checklist"]
        assert (
            output == f"Check: {mock_check_A.name} is now disabled and cannot be used."
        )

    def test_disable_check_project_id_nonexistent_check(
        self, mocker, create_mock_ScanRunner
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True

        mock_ScanRunner.iac_checks = {}
        mock_ScanRunner.persistence_enabled = True

        with pytest.raises(Exception) as e:
            ScanRunner.disable_check(mock_ScanRunner, "mock_check", "valid_project_id")

        assert str(e.value) == f"Nonexistent check: {mock_check.name}"

    def test_configure_check(
        self,
        mocker,
        create_mock_ScanRunner,
        create_mock_UploadFile,
        create_mock_check_config,
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True
        mock_check.configured = False
        mock_check.configure.return_value = CheckOutput(
            f"Check: {mock_check.name} has been configured successfully.", 0
        )  # Successful configure response, since a config_file is present

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = create_mock_check_config()

        assert not list(
            filter(lambda x: x.startswith("mock_check"), os.listdir(env.CONFIG_DIR))
        )

        mock_config = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "test_config.json",
                "content_type": "application/json",
            }
        )

        mock_secret = mocker.MagicMock()
        mock_secret.get_secret_value.return_value = "secret"

        output = ScanRunner.configure_check(
            mock_ScanRunner, "", "mock_check", mock_config, mock_secret
        )

        assert mock_check.configured
        assert output == f"Check: {mock_check.name} has been configured successfully."
        assert os.path.exists(f"{env.CONFIG_DIR}/{mock_check.name}.json")
        
        os.remove(f"{env.CONFIG_DIR}/{mock_check.name}.json")

    def test_configure_check_disabled_check(
        self, mocker, create_mock_ScanRunner, create_mock_UploadFile
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = b'{\n\t"config": "yes"\n}\n'

        mock_config = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "test_config.json",
                "content_type": "application/json",
            }
        )

        mock_secret = mocker.MagicMock()
        mock_secret.get_secret_value.return_value = "secret"

        with pytest.raises(Exception) as e:
            ScanRunner.configure_check(
                mock_ScanRunner, "", "mock_check", mock_config, mock_secret
            )

        assert (
            str(e.value) == f"Check: {mock_check.name} is disabled. You need to enable it first."
        )

    def test_configure_check_nonexistent_check(
        self, mocker, create_mock_ScanRunner, create_mock_UploadFile
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False

        mock_ScanRunner.iac_checks = {}

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = b'{\n\t"config": "yes"\n}\n'

        mock_config = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "test_config.json",
                "content_type": "application/json",
            }
        )

        mock_secret = mocker.MagicMock()
        mock_secret.get_secret_value.return_value = "secret"

        with pytest.raises(Exception) as e:
            ScanRunner.configure_check(
                mock_ScanRunner, "", "mock_check", mock_config, mock_secret
            )

        assert str(e.value) == f"Nonexistent check: {mock_check.name}"

    def test_scan_iac_nonexistent_check(
        self, mocker, create_mock_ScanRunner, create_mock_UploadFile, data_zip_read
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True
        mock_check.configured = True

        mock_ScanRunner.iac_checks = {}

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = data_zip_read

        mock_IaC = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "data.zip",
                "content_type": "application/zip",
            }
        )
        _checks = [mock_check.name]
        with pytest.raises(Exception) as e:
            ScanRunner.scan_iac(mock_ScanRunner, mock_IaC, "", _checks, "json")

        assert (
            str(e.value) == f"Nonexistent, disabled or un-configured checks: {_checks}."
        )

    def test_scan_iac_disabled_check(
        self, mocker, create_mock_ScanRunner, create_mock_UploadFile, data_zip_read
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = False
        mock_check.configured = True

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = data_zip_read

        mock_IaC = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "data.zip",
                "content_type": "application/zip",
            }
        )
        _checks = [mock_check.name]
        with pytest.raises(Exception) as e:
            ScanRunner.scan_iac(mock_ScanRunner, mock_IaC, "", _checks, "json")

        assert (
            str(e.value) == f"Nonexistent, disabled or un-configured checks: {_checks}."
        )

    def test_scan_iac_unconfigured_check(
        self, mocker, create_mock_ScanRunner, create_mock_UploadFile, data_zip_read
    ):
        mock_ScanRunner = create_mock_ScanRunner()

        mock_check = mocker.MagicMock()
        mock_check.name = "mock_check"
        mock_check.enabled = True
        mock_check.configured = False

        mock_ScanRunner.iac_checks = {mock_check.name: mock_check}

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = data_zip_read

        mock_IaC = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "data.zip",
                "content_type": "application/zip",
            }
        )
        _checks = [mock_check.name]
        with pytest.raises(Exception) as e:
            ScanRunner.scan_iac(mock_ScanRunner, mock_IaC, "", _checks, "json")

        assert (
            str(e.value) == f"Nonexistent, disabled or un-configured checks: {_checks}."
        )

    def test_scan_iac(
        self,
        mocker,
        create_mock_ScanRunner,
        create_mock_UploadFile,
        data_zip_read,
        htmlhint_json_response,
        transform_htmlhint,
    ):
        mock_ScanRunner = create_mock_ScanRunner()
        check_output = CheckOutput(htmlhint_json_response, 0)

        htmlhint = mocker.MagicMock()
        htmlhint.name = "htmlhint"
        htmlhint.run.return_value = check_output
        htmlhint.enabled = True
        htmlhint.configured = True

        mock_ScanRunner.iac_checks = {htmlhint.name: htmlhint}
        mock_ScanRunner._init_iac_dir.return_value = None
        mock_ScanRunner._cleanup_iac_dir.return_value = None
        mock_ScanRunner._run_checks.return_value = htmlhint_json_response

        mock_spool = mocker.MagicMock()
        mock_spool.read.return_value = data_zip_read

        mock_IaC = create_mock_UploadFile(
            {
                "file": mock_spool,
                "filename": "data.zip",
                "content_type": "application/zip",
            }
        )

        output = ScanRunner.scan_iac(
            mock_ScanRunner, mock_IaC, "", ["htmlhint"], "json"
        )

        assert transform_htmlhint(output["htmlhint"]) == transform_htmlhint(
            htmlhint_json_response["htmlhint"]
        )

    def test_init_checklist_persistence_enabled(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = []

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"

        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }

        pers_status = os.environ["SCAN_PERSISTENCE"]
        os.environ["SCAN_PERSISTENCE"] = "enabled"
        ScanRunner.init_checklist(mock_ScanRunner)
        os.environ["SCAN_PERSISTENCE"] = pers_status

        assert mock_ScanRunner.project_checklist == [
            mock_check_A.name,
            mock_check_B.name,
        ]

    def test_init_checklist_persistence_disabled(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = []

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"

        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }
        pers_status = os.environ["SCAN_PERSISTENCE"]
        os.environ["SCAN_PERSISTENCE"] = "disabled"
        ScanRunner.init_checklist(mock_ScanRunner)
        os.environ["SCAN_PERSISTENCE"] = pers_status

        assert mock_ScanRunner.project_checklist is None

    def test_set_scan_runner_check(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = ["test", "test", "test"]

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"
        mock_check_A.enabled = True

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"
        mock_check_B.enabled = True

        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }

        ScanRunner.set_scan_runner_check(mock_ScanRunner, [mock_check_B.name])
        assert not mock_check_A.enabled
        assert mock_check_B.enabled
        assert mock_ScanRunner.project_checklist == [mock_check_B.name]

    def test_set_scan_runner_check_empty_checklist(
        self, mocker, create_mock_ScanRunner
    ):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = ["test", "test", "test"]
        output = ScanRunner.set_scan_runner_check(mock_ScanRunner, None)

        assert output is None
        assert mock_ScanRunner.project_checklist is None

    def test_set_scan_checklist(self, mocker, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = ["test", "test", "test"]

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"
        mock_check_A.enabled = False

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"
        mock_check_B.enabled = True

        mock_ScanRunner.iac_checks = {
            mock_check_A.name: mock_check_A,
            mock_check_B.name: mock_check_B,
        }

        ScanRunner.set_scan_checklist(mock_ScanRunner, "")

        assert mock_ScanRunner.project_checklist == [mock_check_B.name]

    def test_set_scan_checklist_project_id(
        self, mocker, create_mock_ScanRunner, load_project_return
    ):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = ["test", "test", "test"]

        mock_check_A = mocker.MagicMock()
        mock_check_A.name = "mock_check_A"
        mock_check_A.enabled = False

        mock_check_B = mocker.MagicMock()
        mock_check_B.name = "mock_check_B"
        mock_check_B.enabled = True

        mock_ScanRunner.scan_project.load_project.return_value = load_project_return(
            [mock_check_A.name, mock_check_B.name]
        )

        ScanRunner.set_scan_checklist(mock_ScanRunner, "valid_project_id")

        assert mock_ScanRunner.project_checklist == [
            mock_check_A.name,
            mock_check_B.name,
        ]

    def test_set_scan_checklist_project_id_empty_checklist(
        self, mocker, create_mock_ScanRunner, load_project_return
    ):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.project_checklist = ["test", "test", "test"]
        mock_ScanRunner.scan_project.load_project.return_value = load_project_return([])
        ScanRunner.set_scan_checklist(mock_ScanRunner, "valid_project_id")
        assert mock_ScanRunner.project_checklist is None

    def test_set_scan_checklist_invalid_project_id(self, create_mock_ScanRunner):
        mock_ScanRunner = create_mock_ScanRunner()
        mock_ScanRunner.scan_project.load_project.side_effect = Exception(
            "Project id does not exist"
        )
        with pytest.raises(Exception) as e:
            ScanRunner.set_scan_checklist(mock_ScanRunner, "invalid_project_id")
        assert str(e.value) == "Project id does not exist"
