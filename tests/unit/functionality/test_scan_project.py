import pytest
import os
import json
from shutil import rmtree

from iac_scan_runner.functionality.scan_project import ScanProject


class TestScanProject:
    # pylint: disable=no-self-use

    def test_insert_project(self, mocker, insert_into_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.mycol.insert_one = insert_into_mock_DB
        result = {
            "project_id": "project_id",
            "creator_id": "creator_id",
            "time": "1/1/1990 00:00:00",
            "active_config": "",
            "checklist": ["mock_check"],
        }
        ScanProject.insert_project(mock_ScanProject, result)
        dir = os.listdir("mock_DB")
        assert len(dir) == 1
        with open("mock_DB/entry.json", "r") as f:
            assert f.read() == json.dumps(result)

        rmtree("mock_DB", True)

    def test_new_project(self, mocker, insert_into_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.mycol.insert_one = insert_into_mock_DB
        mock_uuid = mocker.patch("iac_scan_runner.functionality.scan_project.uuid")
        mock_uuid.uuid4.return_value = "uuid"

        mock_datetime = mocker.patch(
            "iac_scan_runner.functionality.scan_project.datetime"
        )
        mock_datetime.now().strftime.return_value = "1/1/1990 00:00:00"
        id = ScanProject.new_project(mock_ScanProject, "creator_id", "", ["mock_check"])

        assert id == "uuid"
        with open("mock_DB/entry.json", "r") as f:
            content = json.load(f)
        assert content["project_id"] == "uuid"
        assert content["creator_id"] == "creator_id"
        assert content["time"] == "1/1/1990 00:00:00"
        assert content["active_config"] == ""
        assert content["checklist"] == ["mock_check"]
        rmtree("mock_DB", True)

    def test_load_project_valid_project_id(self, mocker, select_from_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.mycol.find_one = select_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "valid_project_id", "checklist": ["mock_check"]}, f
            )
        data = ScanProject.load_project(mock_ScanProject, "valid_project_id")
        assert data["content"] == {
            "project_id": "valid_project_id",
            "checklist": ["mock_check"],
        }
        rmtree("mock_DB")

    def test_load_project_invalid_project_id(self, mocker, select_from_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.mycol.find_one = select_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "valid_project_id", "checklist": ["mock_check"]}, f
            )
        with pytest.raises(Exception) as e:
            ScanProject.load_project(mock_ScanProject, "invalid_project_id")
        assert str(e.value) == "Project id does not exist"
        rmtree("mock_DB")

    def test_add_check_new_check(
        self, mocker, load_project_from_mock_DB, update_in_mock_DB
    ):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.load_project = load_project_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "valid_project_id", "checklist": ["mock_check"]}, f
            )
        mock_ScanProject.mycol.find_one_and_update = update_in_mock_DB
        ScanProject.add_check(mock_ScanProject, "valid_project_id", "new_mock_check")
        with open("mock_DB/entry.json", "r") as f:
            content = json.load(f)
        assert content["checklist"] == ["mock_check", "new_mock_check"]
        rmtree("mock_DB", True)

    def test_add_check_existing_check(
        self, mocker, load_project_from_mock_DB, update_in_mock_DB
    ):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.load_project = load_project_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "valid_project_id", "checklist": ["mock_check"]}, f
            )
        mock_ScanProject.mycol.find_one_and_update = update_in_mock_DB
        ScanProject.add_check(mock_ScanProject, "valid_project_id", "mock_check")
        with open("mock_DB/entry.json", "r") as f:
            content = json.load(f)
        assert content["checklist"] == ["mock_check"]
        rmtree("mock_DB", True)

    def test_add_check_invalid_project_id(self, mocker, load_project_from_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.load_project = load_project_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "valid_project_id", "checklist": ["mock_check"]}, f
            )
        with pytest.raises(Exception) as e:
            ScanProject.add_check(mock_ScanProject, "invalid_project_id", "mock_check")
        assert str(e.value) == "Project id does not exist"
        rmtree("mock_DB", True)

    def test_remove_check(self, mocker, load_project_from_mock_DB, update_in_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.load_project = load_project_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {
                    "project_id": "valid_project_id",
                    "checklist": ["mock_check", "new_mock_check"],
                },
                f,
            )
        mock_ScanProject.mycol.find_one_and_update = update_in_mock_DB
        ScanProject.remove_check(mock_ScanProject, "valid_project_id", "new_mock_check")
        with open("mock_DB/entry.json", "r") as f:
            content = json.load(f)
        assert content["checklist"] == ["mock_check"]
        rmtree("mock_DB", True)

    def test_remove_check_invalid_project_id(self, mocker, load_project_from_mock_DB):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.load_project = load_project_from_mock_DB
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "valid_project_id", "checklist": ["mock_check"]}, f
            )
        with pytest.raises(Exception) as e:
            ScanProject.remove_check(
                mock_ScanProject, "invalid_project_id", "mock_check"
            )
        assert str(e.value) == "Project id does not exist"
        rmtree("mock_DB", True)

    def test_get_project_check_list_valid_project_id(self, mocker, select_from_mock_DB_checklist):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.mycol.find_one = select_from_mock_DB_checklist
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {
                    "project_id": "valid_project_id",
                    "checklist": ["mock_check", "new_mock_check"],
                },
                f,
            )
        output = ScanProject.get_project_check_list(
            mock_ScanProject, "valid_project_id"
        )
        assert output == ["mock_check", "new_mock_check"]
        rmtree("mock_DB", True)

    def test_get_project_check_list_invalid_project_id(self, mocker, select_from_mock_DB_checklist):
        mock_ScanProject = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ScanProject.mycol = mocker.MagicMock()
        mock_ScanProject.mycol.path = "mock_DB"
        mock_ScanProject.mycol.find_one = select_from_mock_DB_checklist
        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {
                    "project_id": "valid_project_id",
                    "checklist": ["mock_check", "new_mock_check"],
                },
                f,
            )
        with pytest.raises(Exception) as e:
            ScanProject.get_project_check_list(mock_ScanProject, "invalid_project_id")
        assert str(e.value) == "Project id does not exist"
        rmtree("mock_DB", True)
