import os
import json
import pytest

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from iac_scan_runner.api import app
from iac_scan_runner.routers import checks
import iac_scan_runner.vars as env

client = TestClient(app)


class TestClass:
    # pylint: disable=no-self-use
    def test_ansible_lint_checks(self, load_response):
        _content = json.loads(load_response("default_get_checks", "json"))
        response = client.get("/default/checks?keyword=ansible-lint")
        assert response.status_code == 200
        assert response.json() == list(
            filter(lambda x: x["name"] == "ansible-lint", _content)
        )

    def test_full_checks(self, load_response):
        _content = load_response("default_get_checks", "json")
        response = client.get("/default/checks")
        assert response.status_code == 200
        assert response.json() == json.loads(_content)

    def test_validation_error_api_call(self):
        response = client.get("/default/checks?configured=foobar")
        assert response.status_code == 422

    def test_not_found_error_api_call(self):
        response = client.get("/defaults/checks/")
        assert response.status_code == 404

    def test_enable_check(
        self,
        re_enable_check,
        enable_check,
    ):
        get_checks_response = client.get("default/checks?configured=true")
        assert get_checks_response.status_code == 200

        checks_list = get_checks_response.json()

        for i in checks_list:
            check_name = i["name"]
            check_status = i["enabled"]

            enable_api_call = "/default/checks/" + check_name + "/enable"

            response = client.put(enable_api_call)
            status_code = response.status_code
            response_content = response.json()

            if check_status:
                assert status_code == 400
                assert response_content == re_enable_check(check_name)
            else:
                assert status_code == 200
                assert response_content == enable_check(check_name)

    def test_disable_check(self, disable_check, re_disable_check):
        get_checks_response = client.get("default/checks")
        assert get_checks_response.status_code == 200

        checks_list = get_checks_response.json()

        for i in checks_list:
            check_name = i["name"]
            check_status = i["enabled"]

            disable_api_call = "/default/checks/" + check_name + "/disable"

            response = client.put(disable_api_call)
            status_code = response.status_code
            response_content = response.json()

            if check_status:
                assert status_code == 200
                assert response_content == disable_check(check_name)
            else:
                assert status_code == 400
                assert response_content == re_disable_check(check_name)

    def test_enable_enabled_check(self, re_enable_check):
        get_checks_response = client.get("default/checks")
        assert get_checks_response.status_code == 200

        checks_list = get_checks_response.json()
        check = checks_list[0]

        check_name = check["name"]

        enable_api_call = "/default/checks/" + check_name + "/enable"

        enable_response = client.put(enable_api_call)
        status_code_enable_response = enable_response.status_code
        assert status_code_enable_response in (200, 400)

        reenable_response = client.put(enable_api_call)
        status_code_reenable_response = reenable_response.status_code
        str_reenable_response = reenable_response.json()

        assert status_code_reenable_response == 400

        assert str_reenable_response == re_enable_check(check_name)

    def test_enable_disabled_check(self, enable_check):
        get_checks_response = client.get("default/checks")
        assert get_checks_response.status_code == 200

        checks_list = get_checks_response.json()
        check = checks_list[0]

        check_name = check["name"]

        disable_api_call = "/default/checks/" + check_name + "/disable"
        enable_api_call = "/default/checks/" + check_name + "/enable"

        disable_response = client.put(disable_api_call)
        status_code_disable_response = disable_response.status_code
        assert (
            status_code_disable_response in (200, 400)
        )

        enable_response = client.put(enable_api_call)
        status_code_enable_response = enable_response.status_code
        str_enable_response = enable_response.json()

        assert status_code_enable_response == 200

        assert str_enable_response == enable_check(check_name)

    def test_disable_enabled_check(self, disable_check):
        get_checks_response = client.get("default/checks")
        assert get_checks_response.status_code == 200

        checks_list = get_checks_response.json()
        check = checks_list[0]

        check_name = check["name"]

        enable_api_call = "/default/checks/" + check_name + "/enable"
        disable_api_call = "/default/checks/" + check_name + "/disable"

        enable_response = client.put(enable_api_call)
        status_code_enable_response = enable_response.status_code
        assert status_code_enable_response in (200, 400)

        disable_response = client.put(disable_api_call)
        status_code_disable_response = disable_response.status_code
        str_disable_response = disable_response.json()

        assert status_code_disable_response == 200

        assert str_disable_response == disable_check(check_name)

    def test_disable_disabled_check(self, re_disable_check):
        get_checks_response = client.get("default/checks")
        assert get_checks_response.status_code == 200

        checks_list = get_checks_response.json()
        check = checks_list[0]

        check_name = check["name"]

        disable_api_call = "/default/checks/" + check_name + "/disable"

        disable_response = client.put(disable_api_call)
        status_code_disable_response = disable_response.status_code
        assert (
            status_code_disable_response in (200, 400)
        )

        redisable_response = client.put(disable_api_call)
        status_code_redisable_response = redisable_response.status_code
        str_redisable_response = redisable_response.json()

        assert status_code_redisable_response == 400

        assert str_redisable_response == re_disable_check(check_name)

    def test_temp_empty_zip_htlmhint(
        self, create_temp_dir, create_temp_archive, empty_htmlhint, clear_outputs
    ):
        temp_dir = create_temp_dir
        temp_dir_path = temp_dir.name
        archive_root_dir = "/tmp"
        archive_name = "test"

        if os.path.exists(f"{archive_name}.zip"):
            os.remove(f"{archive_name}.zip")

        temp_archive = create_temp_archive(archive_root_dir, temp_dir_path, "zip", archive_name)

        iac_file = open(temp_archive["path"], "rb")

        # Save the archive in an UploadFile style touple (filename, file, content-type)
        _iac = (temp_archive["filename"], iac_file, "application/x-xz")

        client.put("/default/checks/htmlhint/enable")

        get_htmlhint = client.get("/default/checks?keyword=htmlhint&enabled=true")
        assert get_htmlhint.json()[0]["enabled"]

        _data = {
            "checks": "htmlhint",
        }
        _files = {"iac": _iac}

        scan_call = "/default/scan?scan_response_type=json"

        # Temporarily change the working directory so that relative
        # paths work as intended and make the API call to scan the files
        generated_html = os.listdir("./outputs/generated_html")
        json_dumps = os.listdir("./outputs/json_dumps")
        logs = os.listdir("./outputs/logs")

        scan_response = client.post(scan_call, data=_data, files=_files)

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(temp_archive["path"])
        _iac[1].close()

        assert scan_response.status_code == 200
        assert scan_response.json()["htmlhint"] == empty_htmlhint["htmlhint"]

    def test_scan_empty_enabled_disabled_check(
        self, create_temp_dir, create_temp_archive, clear_outputs
    ):
        client.put("/default/checks/htmlhint/enable")
        client.put("/default/checks/opera-tosca-parser/disable")

        dir_path = create_temp_dir.name
        archive_root_dir = dir_path[0:dir_path.rfind("/")]
        archive_name = "test"

        if os.path.exists(f"{archive_name}.zip"):
            os.remove(f"{archive_name}.zip")

        temp_zip = create_temp_archive(archive_root_dir, dir_path, "zip", archive_name)
        _iac = (temp_zip["filename"], open(temp_zip["path"], "rb"), "application/zip")

        _data = {"checks": "htmlhint,opera-tosca-parser"}
        _files = {"iac": _iac}

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        scan_response = client.post(
            "/default/scan?scan_response_type=json", data=_data, files=_files
        )

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(temp_zip["path"])
        _iac[1].close()

        assert scan_response.status_code == 400
        assert "opera-tosca-parser" in scan_response.json()

    def test_scan_data_enabled_nonexistent_check(self, create_temp_archive, clear_outputs):
        client.put("/default/checks/htmlhint/enable")
        # The nonexistent check will be "steampunk-scanner"

        archive_root_dir = os.getcwd() + "/tests/data"
        dir_path = archive_root_dir + "/inputs"
        archive_name = "test"

        if os.path.exists(f"{archive_name}.tar"):
            os.remove(f"{archive_name}.tar")

        temp_tar = create_temp_archive(archive_root_dir, dir_path, "tar", archive_name)
        _iac = (temp_tar["filename"], open(temp_tar["path"], "rb"), "application/x-tar")

        _data = {"checks": "htmlhint,steampunk-scanner"}
        _files = {"iac": _iac}

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        scan_response = client.post(
            "/default/scan?scan_response_type=json", data=_data, files=_files
        )

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(temp_tar["path"])
        _iac[1].close()

        assert scan_response.status_code == 400
        assert "steampunk-scanner" in scan_response.json()

    def test_scan_data_unconfigured_check(self, create_temp_archive, clear_outputs):
        """Unconfigured check: steampunk-spotter."""
        archive_root_dir = os.getcwd() + "/tests/data"
        dir_path = archive_root_dir + "/inputs"
        archive_name = "test"

        if os.path.exists(f"{archive_name}.tar.xz"):
            os.remove(f"{archive_name}.tar.xz")

        temp_xztar = create_temp_archive(archive_root_dir, dir_path, "xztar", archive_name)
        _iac = (
            temp_xztar["filename"],
            open(temp_xztar["path"], "rb"),
            "application/x-xz",
        )

        _data = {"checks": "steampunk-spotter"}
        _files = {"iac": _iac}

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        scan_response = client.post(
            "/default/scan?scan_response_type=json", data=_data, files=_files
        )

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(temp_xztar["path"])
        _iac[1].close()

        assert scan_response.status_code == 400
        assert "steampunk-spotter" in scan_response.json()

    def test_scan_data_unconfigured_nonexistent_check(self, create_temp_archive, clear_outputs):
        """Nonexistent check: steampunk-scanner."""
        archive_root_dir = os.getcwd() + "/tests/data"
        dir_path = archive_root_dir + "/inputs"
        archive_name = "test"

        if os.path.exists(f"{archive_name}.tar.xz"):
            os.remove(f"{archive_name}.tar.xz")

        temp_xztar = create_temp_archive(archive_root_dir, dir_path, "xztar", archive_name)
        _iac = (
            temp_xztar["filename"],
            open(temp_xztar["path"], "rb"),
            "application/x-xz",
        )

        _data = {"checks": "steampunk-scanner"}
        _files = {"iac": _iac}

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        scan_response = client.post(
            "/default/scan?scan_response_type=json", data=_data, files=_files
        )

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(temp_xztar["path"])
        _iac[1].close()

        assert scan_response.status_code == 400
        assert "steampunk-scanner" in scan_response.json()

    def test_htmlhint_scan(self, create_temp_archive, load_response, transform_check, clear_outputs):
        htmlhint_response = json.loads(load_response("default_full_scan", "json"))[
            "htmlhint"
        ]
        htmlhint_response = transform_check("htmlhint", htmlhint_response)
        archive_root_dir = os.getcwd() + "/tests/data"
        dir_path = archive_root_dir + "/inputs"
        archive_name = "test"

        if os.path.exists(f"{archive_name}.zip"):
            os.remove(f"{archive_name}.zip")

        temp_zip = create_temp_archive(archive_root_dir, dir_path, "zip", archive_name)
        _iac = (temp_zip["filename"], open(temp_zip["path"], "rb"), "application/zip")

        _data = {"checks": "htmlhint"}
        _files = {"iac": _iac}

        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        scan_response = client.post(
            "/default/scan?scan_response_type=json", data=_data, files=_files
        )

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(temp_zip["path"])
        _iac[1].close()

        scan_response_htmlhint = transform_check(
            "htmlhint", scan_response.json()["htmlhint"]
        )

        assert scan_response.status_code == 200
        assert scan_response_htmlhint == htmlhint_response

    def test_empty_zip_html_response(
        self, create_temp_dir, create_temp_archive, load_response, trim_html_response, clear_outputs
    ):

        empty_html_response = trim_html_response(
            load_response("default_empty_scan", "html")
        )
        dir_path = create_temp_dir
        archive_root_dir = "/tmp"
        archive_name = "test"

        if os.path.exists(f"/tests/integration/{archive_name}"):
            os.remove(f"/tests/integration/{archive_name}")

        test_zip = create_temp_archive(archive_root_dir, dir_path.name, "zip", archive_name)
        iac_file = open(test_zip["path"], "rb")
        _iac = (test_zip["filename"], iac_file, "application/zip")
        client.put("/default/checks/htmlhint/enable")
        _data = {
            "checks": "htmlhint",
        }

        _files = {"iac": _iac}

        scan_call = "/default/scan?scan_response_type=html"

        # Temporarily change the working directory so that relative
        # paths work as intended and make the API call to scan the files
        generated_html = os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")
        json_dumps = os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")
        logs = os.listdir(f"{env.ROOT_DIR}/outputs/logs")

        scan_response = client.post(scan_call, data=_data, files=_files)

        clear_outputs(generated_html, json_dumps, logs)

        os.remove(test_zip["path"])
        _iac[1].close()

        status_code_scan_response = scan_response.status_code
        assert status_code_scan_response == 200
        response_content = trim_html_response(scan_response.content.decode())
        assert response_content == empty_html_response

    @pytest.mark.asyncio
    async def test_configure_steampunk_spotter_disabled(
        self, mocker, configure_disabled_check
    ):
        mocker.patch("iac_scan_runner.routers.checks.put_configure_check")

        checks.put_configure_check.return_value = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=configure_disabled_check("steampunk-spotter"),
        )
        config_response = await checks.put_configure_check(
            check_name="steampunk-spotter"
        )
        config_response_json = json.loads(config_response.body)
        checks.put_configure_check.assert_called_with(check_name="steampunk-spotter")
        assert config_response_json == configure_disabled_check("steampunk-spotter")

    @pytest.mark.asyncio
    async def test_configure_steampunk_spotter_no_data(
        self,
        mocker,
    ):
        mocker.patch("iac_scan_runner.routers.checks.put_configure_check")

        checks.put_configure_check.return_value = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Check: steampunk-spotter requires you to pass user token and an optional configuration file.",
        )
        config_response = await checks.put_configure_check(
            check_name="steampunk-spotter"
        )
        config_response_json = json.loads(config_response.body)
        checks.put_configure_check.assert_called_with(check_name="steampunk-spotter")
        assert (
            config_response_json == "Check: steampunk-spotter "
            "requires you to pass user token and an optional configuration file."
        )

    @pytest.mark.asyncio
    async def test_configure_steampunk_spotter_wrong_token(
        self,
        mocker,
    ):
        mocker.patch("iac_scan_runner.routers.checks.put_configure_check")

        checks.put_configure_check.return_value = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Check: steampunk-spotter something went wrong with login. Maybe you used wrong token.",
        )
        config_response = await checks.put_configure_check(
            check_name="steampunk-spotter", form_data={"secret": "wrong-api-token"}
        )
        config_response_json = json.loads(config_response.body)
        checks.put_configure_check.assert_called_with(
            check_name="steampunk-spotter", form_data={"secret": "wrong-api-token"}
        )
        assert (
            config_response_json == "Check: steampunk-spotter "
            "something went wrong with login. Maybe you used wrong token."
        )

    @pytest.mark.asyncio
    async def test_configure_steampunk_spotter_successful(
        self,
        mocker,
    ):
        mocker.patch("iac_scan_runner.routers.checks.put_configure_check")

        checks.put_configure_check.return_value = JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Check: steampunk-spotter has been configured successfully.",
        )
        config_response = await checks.put_configure_check(
            check_name="steampunk-spotter", data={"secret": "api-token"}
        )
        config_response_json = json.loads(config_response.body)
        checks.put_configure_check.assert_called_with(
            check_name="steampunk-spotter", data={"secret": "api-token"}
        )
        assert (
            config_response_json == "Check: steampunk-spotter "
            "has been configured successfully."
        )
