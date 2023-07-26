import os
import json

from shutil import rmtree
from iac_scan_runner.functionality.project_config import ProjectConfig


class TestProjectConfig:
    # pylint: disable=no-self-use

    def test_insert_config(self, mocker, insert_into_mock_DB):
        mock_project = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        mock_project.mycol.insert_one = insert_into_mock_DB
        result = {"config": "test"}
        ProjectConfig.insert_config(mock_project, result)
        dir = os.listdir("mock_DB")
        assert len(dir) == 1
        with open("mock_DB/entry.json", "r") as f:
            assert f.read() == json.dumps(result)

        rmtree("mock_DB", True)

    def test_new_config(self, mocker, insert_into_mock_DB):
        mock_project = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_project.mycol.insert_one = insert_into_mock_DB

        _creator_id = "creator_id"
        _parameters = {"parameter_a": "a", "parameter_b": "b"}

        _config_id = ProjectConfig.new_config(
            mock_project, creator_id=_creator_id, parameters=_parameters
        )
        dir = os.listdir("mock_DB")
        assert len(dir) == 1
        with open("mock_DB/entry.json", "r") as f:
            content = json.loads(f.read())
        assert list(content.keys()) == ["config_id", "creator_id", "parameters"]
        assert content["creator_id"] == _creator_id
        assert content["parameters"] == _parameters
        assert content["config_id"] == _config_id

        rmtree("mock_DB", True)

    def test_load_config(self, mocker, select_from_mock_DB):
        mock_project = mocker.MagicMock()
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        with open(f"{mock_project.mycol.path}/entry.json", "w") as f:
            content = {
                "config_id": "1",
                "creator_id": "test_id",
                "parameters": {"ping": "pong"},
            }
            json.dump(content, f)

        mock_project.mycol.find_one = select_from_mock_DB
        config = ProjectConfig.load_config(mock_project, "1")
        assert config["content"] == content

        rmtree("mock_DB", True)

    def test_load_config_no_mycol(self, mocker):
        mock_project = mocker.MagicMock()
        mock_project.mycol = None

        output = ProjectConfig.load_config(mock_project, "none")
        assert output is None

    def test_set_parameters(self, mocker, update_in_mock_DB):
        mock_project = mocker.MagicMock()
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open(f"{mock_project.mycol.path}/entry.json", "w") as f:
            content = {
                "config_id": "1",
                "creator_id": "test_id",
                "parameters": {"ping": "pong"},
            }
            json.dump(content, f)

        mock_project.mycol.find_one_and_update = update_in_mock_DB
        ProjectConfig.set_parameters(mock_project, "1", {"bing": "bong"})

        with open(f"{mock_project.mycol.path}/entry.json", "r") as f:
            content = json.load(f)

        assert content["parameters"] == {"bing": "bong"}
        rmtree("mock_DB")

    def test_set_parameters_nonexistent_config_id(self, mocker, update_in_mock_DB):
        mock_project = mocker.MagicMock()
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open(f"{mock_project.mycol.path}/entry.json", "w") as f:
            content = {
                "config_id": "1",
                "creator_id": "test_id",
                "parameters": {"ping": "pong"},
            }
            json.dump(content, f)

        mock_project.mycol.find_one_and_update = update_in_mock_DB
        ProjectConfig.set_parameters(mock_project, "2", {"bing": "bong"})

        with open(f"{mock_project.mycol.path}/entry.json", "r") as f:
            new_content = json.load(f)
        assert content == new_content

        with open(f"{mock_project.mycol.path}/update.json", "r") as f:
            update_content = json.load(f)
        assert update_content["parameters"] == {"bing": "bong"}
        assert update_content["config_id"] == "2"
        rmtree("mock_DB")

    def test_delete_config(self, mocker, delete_from_mock_DB):
        mock_project = mocker.MagicMock()
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        filename = "entry.json"
        with open(f"{mock_project.mycol.path}/{filename}", "w") as f:
            content = {
                "config_id": "1",
                "creator_id": "test_id",
                "parameters": {"ping": "pong"},
            }
            json.dump(content, f)

        mock_project.mycol.delete_one = delete_from_mock_DB
        ProjectConfig.delete_config(mock_project, "1")

        assert not os.path.isfile(f"mock_DB/{filename}")
        assert not len(os.listdir("mock_DB"))
        rmtree("mock_DB")

    def test_delete_nonexistent_DB(self, mocker, delete_from_mock_DB):
        mock_project = mocker.MagicMock()
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        filename = "entry.json"
        with open(f"{mock_project.mycol.path}/{filename}", "w") as f:
            content = {
                "config_id": "1",
                "creator_id": "test_id",
                "parameters": {"ping": "pong"},
            }
            json.dump(content, f)

        mock_project.mycol.delete_one = delete_from_mock_DB
        ProjectConfig.delete_config(mock_project, "2")

        assert os.path.isfile(f"mock_DB/{filename}")
        assert len(os.listdir("mock_DB")) == 1
        rmtree("mock_DB")

    def test_all_configs(self, mocker, find_all):
        mock_project = mocker.MagicMock()
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        filename = "entry_1.json"
        with open(f"{mock_project.mycol.path}/{filename}", "w") as f:
            content = {
                "config_id": "1",
                "creator_id": "test_id",
                "parameters": {"ping": "pong"},
            }
            json.dump(content, f)
        filename = "entry_2.json"
        with open(f"{mock_project.mycol.path}/{filename}", "w") as f:
            content_2 = content
            content_2["config_id"] = "2"
            content_2["creator_id"] = "another_test_id"
            json.dump(content_2, f)

        mock_project.mycol.find = find_all
        output = ProjectConfig.all_configs(mock_project)
        assert str(content) in output
        assert str(content_2) in output
        rmtree("mock_DB")

    def test_all_configs_empty_db(self, mocker, find_all):
        mock_project = mocker.MagicMock()
        mock_project.mycol = mocker.MagicMock()
        mock_project.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_project.mycol.find = find_all
        output = ProjectConfig.all_configs(mock_project)
        assert output == ""
        rmtree("mock_DB")
