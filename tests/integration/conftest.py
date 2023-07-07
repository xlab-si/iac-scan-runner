import shutil
import os
import tempfile
import pytest
from fastapi import UploadFile
import iac_scan_runner.vars as env


@pytest.fixture
def load_response():
    def _load_response(response, content_type):
        filename = f"{response}.{content_type}"
        path = os.getcwd() + "/tests/data/outputs/"
        with open(file=(path + filename), mode="r", encoding="utf-8") as f:
            content = f.read()
        return content

    return _load_response


@pytest.fixture
def empty_htmlhint():
    return {
        "htmlhint": {
            "status": "No files",
            "log": "",
            "files": ""
        }
    }


@pytest.fixture
def create_temp_dir():
    return tempfile.TemporaryDirectory()


@pytest.fixture
def create_temp_file():
    def _create_temp_file(dir_path, extension):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=f".{extension}", dir=dir_path
        )
        return tmp

    return _create_temp_file


@pytest.fixture
def create_temp_archive():
    def _create_temp_archive(root_dir, dir_path, extension, archive_name="test"):
        cwd = os.getcwd()
        # Relative (spremeni na env.ROOT_DIR/tests/integration/test)
        archive_path = f"{cwd}/tests/integration/{archive_name}"
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
        return {
            "path": f"tests/integration/{archive_name}.{extension}",
            "filename": f"{archive_name}.{extension}",
        }

    return _create_temp_archive


@pytest.fixture
def configure_disabled_check():
    def _configure_disabled_check(check):
        return f"Check: {check} is disabled. You need to enable it first."

    return _configure_disabled_check


@pytest.fixture
def project_invalid_id():
    return "Project id does not exist"


@pytest.fixture
def project_validation_error():
    return {
        "detail": [
            {
                "loc": ["query", "enabled"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            }
        ]
    }


@pytest.fixture
def disable_check():
    def _project_disable_check(check_name):
        return f"Check: {check_name} is now disabled and cannot be used."

    return _project_disable_check


@pytest.fixture
def enable_check():
    def _project_enable_check(check_name):
        return f"Check: {check_name} is now enabled and available to use."

    return _project_enable_check


@pytest.fixture
def re_enable_check():
    def _re_enable_check(check_name):
        return f"Check: {check_name} is already enabled."

    return _re_enable_check


@pytest.fixture
def re_disable_check():
    def _re_disable_check(check_name):
        return f"Check: {check_name} is already disabled."

    return _re_disable_check


@pytest.fixture
def nonexistent_check():
    def _nonexistent_check(check_name):
        return f"Nonexistent check: {check_name}"

    return _nonexistent_check


@pytest.fixture
def project_make_upload_file():
    def _make_upload_file(_filename, _content_type, origin):
        _file = tempfile.SpooledTemporaryFile(mode="wb", suffix=".zip")
        with open(origin, "rb") as f:
            _file.write(f.read())

        upload_file = UploadFile(filename=_filename, content_type=_content_type, file=_file)
        return upload_file

    return _make_upload_file


@pytest.fixture
def transform_check(
    transform_git_leaks,
    transform_bandit,
    transform_checkstyle,
    transform_cloc,
    transform_htmlhint,
):
    def _transform(
        check,
        content,
    ):
        func = {
            "git-leaks": transform_git_leaks,
            "bandit": transform_bandit,
            "checkstyle": transform_checkstyle,
            "cloc": transform_cloc,
            "htmlhint": transform_htmlhint,
        }
        return func[check](content)

    return _transform


@pytest.fixture
def transform_git_leaks():
    def _transform(content):
        content = content["log"].split("\n")[1:3]
        for i in range(2):
            content[i] = content[i][content[i].index("level"): len(content[i])]
        return content

    return _transform


@pytest.fixture
def transform_bandit():
    def _transform(content):
        content = content[content.index("Test results:"): len(content)]
        content = content["log"].split("\n")
        return content

    return _transform


@pytest.fixture
def transform_checkstyle():
    def _transform(content):
        content = content["log"].split("\n")
        for i, item in enumerate(content):
            content[i] = item.split(":", 1)
            if len(item) > 1:
                content[i] = item[1]
            else:
                content[i] = item[0]
        return content
    return _transform


@pytest.fixture
def transform_cloc():
    def _transform(content):
        content = content["log"].split("-", 1)[1]
        return content

    return _transform


@pytest.fixture
def transform_htmlhint():
    def _transform(content):
        content = content["log"]
        end = content.rfind("(")
        start = content.index(".html")
        content = content[start:end]
        return content

    return _transform


@pytest.fixture
def trim_html_response():
    def _trim(content):
        _content = content.split("\n")
        trimmed_content = []
        trim = False
        start = 0
        end = len(_content) - 1
        for i, item in enumerate(_content):
            if '<div class="container">' in item:
                start = i
                trim = True
            if trim is True and "</div>" in item:
                end = i
                trim = False
                break
        trimmed_content = _content[0:start] + _content[end + 1:len(_content)]
        _content = "\n".join(trimmed_content)
        return _content

    return _trim


@pytest.fixture
def clear_outputs():
    def _clear_outputs(
        generated_html, json_dumps, logs
    ):
        new_html = list(filter(lambda x: x not in generated_html,
                               os.listdir(f"{env.ROOT_DIR}/outputs/generated_html")))
        if new_html:
            os.remove(f"{env.ROOT_DIR}/outputs/generated_html/{new_html[0]}")
        new_json = list(filter(lambda x: x not in json_dumps,
                               os.listdir(f"{env.ROOT_DIR}/outputs/json_dumps")))
        if new_json:
            os.remove(f"{env.ROOT_DIR}/outputs/json_dumps/{new_json[0]}")
        new_log = list(filter(lambda x: x not in logs,
                              os.listdir(f"{env.ROOT_DIR}/outputs/logs")))
        if new_log:
            shutil.rmtree(f"{env.ROOT_DIR}/outputs/logs/{new_log[0]}")
    return _clear_outputs
