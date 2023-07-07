import json
import os
import pytest

from fastapi import status
from fastapi.responses import JSONResponse
from iac_scan_runner.routers import project
from iac_scan_runner.model.Scan import ScanModel


class TestProjectClass:
    # pylint: disable=no-self-use

    @pytest.mark.asyncio
    async def test_new_project_no_creator_id(self, mocker):
        # pylint: disable=no-value-for-parameter
        mocker.patch("iac_scan_runner.routers.project.post_new_project")
        project.post_new_project.return_value = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": ["query", "creator_id"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        )

        new_project_response = await project.post_new_project()

        project.post_new_project.assert_called_with()
        assert new_project_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert json.loads(new_project_response.body) == {
            "detail": [
                {
                    "loc": ["query", "creator_id"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_new_project(self, mocker):
        mocker.patch("iac_scan_runner.routers.project.post_new_project")
        project.post_new_project.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content="uuid"
        )

        new_project_response = await project.post_new_project(creator_id="some_string")

        project.post_new_project.assert_called_with(creator_id="some_string")
        assert new_project_response.status_code == status.HTTP_200_OK
        assert json.loads(new_project_response.body) == "uuid"

    @pytest.mark.asyncio
    async def test_get_all_checks_valid_id(self, mocker, load_response):
        _content = json.loads(load_response("project_get_checks", "json"))
        mocker.patch("iac_scan_runner.routers.project.get_checks")
        project.get_checks.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )
        _project_id = "valid_id"
        get_checks_response = await project.get_checks(project_id=_project_id)

        project.get_checks.assert_called_with(project_id=_project_id)
        assert get_checks_response.status_code == status.HTTP_200_OK
        assert json.loads(get_checks_response.body) == _content

    @pytest.mark.asyncio
    async def test_get_all_checks_invalid_id(self, mocker, project_invalid_id):
        mocker.patch("iac_scan_runner.routers.project.get_checks")
        project.get_checks.return_value = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=project_invalid_id
        )
        _project_id = "invalid_id"
        get_checks_response = await project.get_checks(project_id=_project_id)

        project.get_checks.assert_called_with(project_id=_project_id)
        assert get_checks_response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(get_checks_response.body) == project_invalid_id

    @pytest.mark.asyncio
    async def test_get_disabled_checks(self, mocker, load_response):
        _content = list(
            filter(
                lambda x: not x["enabled"],
                json.loads(load_response("project_get_checks", "json")),
            )
        )
        mocker.patch("iac_scan_runner.routers.project.get_checks")
        project.get_checks.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )
        _project_id = "valid_id"
        get_checks_response = await project.get_checks(
            project_id=_project_id, enabled="false"
        )

        project.get_checks.assert_called_with(project_id=_project_id, enabled="false")
        assert get_checks_response.status_code == status.HTTP_200_OK
        assert json.loads(get_checks_response.body) == _content

    @pytest.mark.asyncio
    async def test_get_unconfigured_checks(self, mocker, load_response):
        _content = list(
            filter(
                lambda x: not x["configured"],
                json.loads(load_response("project_get_checks", "json")),
            )
        )
        mocker.patch("iac_scan_runner.routers.project.get_checks")
        project.get_checks.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )
        _project_id = "valid_id"
        get_checks_response = await project.get_checks(
            project_id=_project_id, configured="false"
        )

        project.get_checks.assert_called_with(
            project_id=_project_id, configured="false"
        )
        assert get_checks_response.status_code == status.HTTP_200_OK
        assert json.loads(get_checks_response.body) == _content

    @pytest.mark.asyncio
    async def test_get_iac_and_component_checks(self, mocker, load_response):
        _content = list(
            filter(
                lambda x: x["target_entity_type"] == "IaC and component",
                json.loads(load_response("project_get_checks", "json")),
            )
        )
        mocker.patch("iac_scan_runner.routers.project.get_checks")
        project.get_checks.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )
        _project_id = "valid_id"
        get_checks_response = await project.get_checks(
            project_id=_project_id, target_entity_type="IaC and component"
        )

        project.get_checks.assert_called_with(
            project_id=_project_id, target_entity_type="IaC and component"
        )
        assert get_checks_response.status_code == status.HTTP_200_OK
        assert json.loads(get_checks_response.body) == _content

    @pytest.mark.asyncio
    async def test_get_enabled_configured_checks(self, mocker, load_response):
        _content = list(
            filter(
                lambda x: x["enabled"] and x["configured"],
                json.loads(load_response("project_get_checks", "json")),
            )
        )
        mocker.patch("iac_scan_runner.routers.project.get_checks")
        project.get_checks.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )
        _project_id = "valid_id"
        get_checks_response = await project.get_checks(
            project_id=_project_id, enabled="true", configured="true"
        )

        project.get_checks.assert_called_with(
            project_id=_project_id, enabled="true", configured="true"
        )
        assert get_checks_response.status_code == status.HTTP_200_OK
        assert json.loads(get_checks_response.body) == _content

    @pytest.mark.asyncio
    async def test_disable_all_checks(self, mocker, load_response, disable_check):
        project_get_all_checks_response = json.loads(
            load_response("project_get_checks", "json")
        )
        mocker.patch("iac_scan_runner.routers.project.put_disable_checks")
        _project_id = "valid_id"

        for i in project_get_all_checks_response:
            _check_name = i["name"]
            project.put_disable_checks.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content=disable_check(_check_name),
            )
            put_disable_response = await project.put_disable_checks(
                project_id=_project_id, check_name=_check_name
            )

            project.put_disable_checks.assert_called_with(
                project_id=_project_id, check_name=_check_name
            )
            assert put_disable_response.status_code == status.HTTP_200_OK
            assert json.loads(put_disable_response.body) == disable_check(_check_name)

    @pytest.mark.asyncio
    async def test_enable_all_checks(self, mocker, load_response, enable_check):
        project_get_all_checks_response = json.loads(
            load_response("project_get_checks", "json")
        )
        mocker.patch("iac_scan_runner.routers.project.put_enable_checks")
        _project_id = "valid_id"

        for i in project_get_all_checks_response:
            _check_name = i["name"]
            project.put_enable_checks.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content=enable_check(_check_name),
            )
            put_enable_checks_response = await project.put_enable_checks(
                project_id=_project_id, check_name=_check_name
            )

            project.put_enable_checks.assert_called_with(
                project_id=_project_id, check_name=_check_name
            )
            assert put_enable_checks_response.status_code == status.HTTP_200_OK
            assert json.loads(put_enable_checks_response.body) == enable_check(
                _check_name
            )

    @pytest.mark.asyncio
    async def test_enable_nonexistent_check(self, mocker, nonexistent_check):
        mocker.patch("iac_scan_runner.routers.project.put_enable_checks")
        _project_id = "valid_id"
        _check_name = "nonexistent"

        project.put_enable_checks.return_value = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=nonexistent_check(_check_name),
        )

        enable_response = await project.put_enable_checks(
            project_id=_project_id, check_name=_check_name
        )

        project.put_enable_checks.assert_called_with(
            project_id=_project_id, check_name=_check_name
        )

        assert enable_response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(enable_response.body) == nonexistent_check(_check_name)

    @pytest.mark.asyncio
    async def test_disable_nonexistent_check(self, mocker, nonexistent_check):
        mocker.patch("iac_scan_runner.routers.project.put_disable_checks")
        _project_id = "valid_id"
        _check_name = "nonexistent"

        project.put_disable_checks.return_value = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=nonexistent_check(_check_name),
        )

        disable_response = await project.put_disable_checks(
            project_id=_project_id, check_name=_check_name
        )

        project.put_disable_checks.assert_called_with(
            project_id=_project_id, check_name=_check_name
        )

        assert disable_response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(disable_response.body) == nonexistent_check(_check_name)

    @pytest.mark.asyncio
    async def test_temp_zip_htlmhint(
        self,
        mocker,
        create_temp_archive,
        project_make_upload_file,
        transform_check,
        load_response,
    ):
        _content = json.loads(load_response("project_full_scan", "json"))
        _content["htmlhint"]["log"] = transform_check("htmlhint", _content["htmlhint"])
        _content["uuid"] = "scan_uuid"

        archive_root_dir = os.getcwd() + "/tests/data"
        archive_name = "test"
        dir_path = archive_root_dir + "/data/inputs"

        temp_zip = create_temp_archive(archive_root_dir, dir_path, "zip", archive_name)

        mocker.patch("iac_scan_runner.routers.project.post_scan")
        _project_id = "valid_id"
        project.post_scan.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )
        _iac = project_make_upload_file("empty.zip", "application/zip", temp_zip["path"])
        os.remove(temp_zip["path"])
        _form_data = ScanModel(iac=_iac)

        post_scan_response = await project.post_scan(
            project_id=_project_id, form_data=_form_data, scan_response_type="json"
        )

        project.post_scan.assert_called_with(
            project_id=_project_id, form_data=_form_data, scan_response_type="json"
        )

        assert post_scan_response.status_code == status.HTTP_200_OK
        assert json.loads(post_scan_response.body)["htmlhint"] == _content["htmlhint"]
        assert json.loads(post_scan_response.body)["uuid"] == _content["uuid"]

    @pytest.mark.asyncio
    async def test_scan_results(
        self,
        mocker,
        load_response,
    ):
        _content = json.loads(load_response("project_full_scan_result", "json"))
        _content = json.loads(_content)

        mocker.patch("iac_scan_runner.routers.project.get_scan_result")
        _project_id = "valid_id"
        _uuid = "scan_uuid"
        project.get_scan_result.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )

        get_scan_result_response = await project.get_scan_result(
            uuid=_uuid, project_id=_project_id
        )

        project.get_scan_result.assert_called_with(uuid=_uuid, project_id=_project_id)

        assert get_scan_result_response.status_code == status.HTTP_200_OK
        assert json.loads(get_scan_result_response.body) == _content

    @pytest.mark.asyncio
    async def test_delete_results(
        self,
        mocker,
    ):
        _content = "null"

        mocker.patch("iac_scan_runner.routers.project.delete_scan_result")
        _uuid = "scan_uuid"
        project.delete_scan_result.return_value = JSONResponse(
            status_code=status.HTTP_200_OK, content=_content
        )

        delete_scan_result_response = await project.delete_scan_result(uuid=_uuid)

        project.delete_scan_result.assert_called_with(uuid=_uuid)

        assert delete_scan_result_response.status_code == status.HTTP_200_OK
        assert json.loads(delete_scan_result_response.body) == _content
