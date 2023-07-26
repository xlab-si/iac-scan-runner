import pytest
import os
import json

from shutil import rmtree
from iac_scan_runner.functionality.results_persistence import ResultsPersistence


class TestResultsPersistence:
    # pylint: disable=no-self-use

    def test_insert_result(self, mocker, insert_into_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        mock_ResultsPersistence.mycol.insert_one = insert_into_mock_DB
        result = {"mock_check": {}, "uuid": "uuid"}

        ResultsPersistence.insert_result(mock_ResultsPersistence, result)
        with open("mock_DB/entry.json", "r") as f:
            content = json.load(f)

        assert content == result
        rmtree("mock_DB", True)

    def test_insert_result_no_col(self, mocker):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = None
        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")
        ResultsPersistence.insert_result(mock_ResultsPersistence, {})
        assert len(os.listdir("mock_DB")) == 0
        rmtree("mock_DB", True)

    def test_show_result(self, mocker, select_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump({"mock_check": {}, "uuid": "uuid4"}, f)

        mock_ResultsPersistence.mycol.find_one = select_from_mock_DB

        data = ResultsPersistence.show_result(mock_ResultsPersistence, "uuid4")
        assert data["content"] == {"mock_check": {}, "uuid": "uuid4"}
        rmtree("mock_DB", True)

    def test_show_result_invalid_uuid(self, mocker, select_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump({"mock_check": {}, "uuid": "uuid4"}, f)

        mock_ResultsPersistence.mycol.find_one = select_from_mock_DB
        with pytest.raises(Exception) as e:
            ResultsPersistence.show_result(
                mock_ResultsPersistence, "invalid_uuid4"
            )
        assert str(e.value) == "Project id does not exist or there are no scan results"
        rmtree("mock_DB", True)

    def test_delete_result(self, mocker, delete_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump({"mock_check": {}, "uuid": "uuid4"}, f)

        mock_ResultsPersistence.mycol.delete_one = delete_from_mock_DB
        ResultsPersistence.delete_result(mock_ResultsPersistence, "uuid4")
        assert len(os.listdir("mock_DB")) == 0
        rmtree("mock_DB", True)

    def test_delete_result_nonexistent_scan(self, mocker, delete_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump({"mock_check": {}, "uuid": "uuid4"}, f)

        mock_ResultsPersistence.mycol.delete_one = delete_from_mock_DB
        ResultsPersistence.delete_result(mock_ResultsPersistence, "nonexistent_uuid4")
        assert len(os.listdir("mock_DB")) == 1
        rmtree("mock_DB", True)

    def test_show_all(self, mocker, find_all):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump({"mock_check": {}, "uuid": "uuid4"}, f)
        with open("mock_DB/entry2.json", "w") as f:
            json.dump(
                {
                    "mock_check": {
                        "status": "Passed",
                        "files": "test.mock",
                        "log": "Ok",
                    },
                    "uuid": "uuid8",
                },
                f,
            )

        mock_ResultsPersistence.mycol.find = find_all
        output = ResultsPersistence.show_all(mock_ResultsPersistence)
        assert (
            output == "{'mock_check': {'status': 'Passed', 'files': 'test.mock', 'log': 'Ok'}, 'uuid': 'uuid8'}"
            "{'mock_check': {}, 'uuid': 'uuid4'}"
        )
        rmtree("mock_DB", True)

    def test_result_age(self, mocker, select_from_mock_DB_content, date_mock):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"mock_check": {}, "uuid": "uuid4", "time": "1/1/1990, 00:00:00"}, f
            )
        mock_ResultsPersistence.mycol.find = select_from_mock_DB_content
        mock_days = mocker.patch(
            "iac_scan_runner.functionality.results_persistence.days_passed"
        )
        mock_days.side_effect = date_mock
        days = ResultsPersistence.result_age(mock_ResultsPersistence, "uuid4")
        assert days == 4
        rmtree("mock_DB", True)

    def test_periodic_clean_job_young(self, mocker, find_all, delete_from_mock_DB_uuid):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"mock_check": {}, "uuid": "uuid4", "time": "1/1/1990, 00:00:00"}, f
            )
        mock_ResultsPersistence.mycol.find = find_all
        mock_ResultsPersistence.mycol.delete_result = delete_from_mock_DB_uuid
        mock_ResultsPersistence.result_age.return_value = 4

        ResultsPersistence.periodic_clean_job(mock_ResultsPersistence)
        assert len(os.listdir("mock_DB")) == 1
        rmtree("mock_DB", True)

    def test_periodic_clean_job_old(self, mocker, find_all, delete_from_mock_DB_uuid):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        mock_ResultsPersistence.mycol.find = find_all
        mock_ResultsPersistence.mycol.delete_result = delete_from_mock_DB_uuid
        mock_ResultsPersistence.result_age.return_value = 16

        ResultsPersistence.periodic_clean_job(mock_ResultsPersistence)
        assert len(os.listdir("mock_DB")) == 0
        rmtree("mock_DB", True)

    def test_get_scan_result(self, mocker, select_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "project_id", "mock_check": {}, "uuid": "uuid4"}, f
            )
        with open("mock_DB/entry2.json", "w") as f:
            json.dump(
                {
                    "project_id": "project_id",
                    "mock_check": {"status": "Passed"},
                    "uuid": "uuid8",
                },
                f,
            )

        mock_ResultsPersistence.mycol.find_one = select_from_mock_DB
        data = ResultsPersistence.get_scan_result(
            mock_ResultsPersistence, "project_id", "uuid4"
        )
        assert data["content"] == {
            "project_id": "project_id",
            "mock_check": {},
            "uuid": "uuid4",
        }
        rmtree("mock_DB", True)

    def test_get_scan_result_invalid_project_id(self, mocker, select_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "project_id", "mock_check": {}, "uuid": "uuid4"}, f
            )
        with open("mock_DB/entry2.json", "w") as f:
            json.dump(
                {
                    "project_id": "project_id",
                    "mock_check": {"status": "Passed"},
                    "uuid": "uuid8",
                },
                f,
            )

        mock_ResultsPersistence.mycol.find_one = select_from_mock_DB
        with pytest.raises(Exception) as e:
            ResultsPersistence.get_scan_result(
                mock_ResultsPersistence, "invalid_project_id", "uuid4"
            )
        assert (
            str(e.value) == "Project id or uuid does not exist or there are no scan results"
        )
        rmtree("mock_DB", True)

    def test_get_scan_result_invalid_uuid(self, mocker, select_from_mock_DB):
        mock_ResultsPersistence = mocker.MagicMock()
        mock_ResultsPersistence.mycol = mocker.MagicMock()
        mock_ResultsPersistence.mycol.path = "mock_DB"

        if not os.path.exists(f"{os.getcwd()}/mock_DB"):
            os.mkdir("mock_DB")

        with open("mock_DB/entry.json", "w") as f:
            json.dump(
                {"project_id": "project_id", "mock_check": {}, "uuid": "uuid4"}, f
            )
        with open("mock_DB/entry2.json", "w") as f:
            json.dump(
                {
                    "project_id": "project_id",
                    "mock_check": {"status": "Passed"},
                    "uuid": "uuid8",
                },
                f,
            )

        mock_ResultsPersistence.mycol.find_one = select_from_mock_DB
        with pytest.raises(Exception) as e:
            ResultsPersistence.get_scan_result(
                mock_ResultsPersistence, "project_id", "invalid_uuid"
            )
        assert (
            str(e.value) == "Project id or uuid does not exist or there are no scan results"
        )
        rmtree("mock_DB", True)
