import os
import json
import shutil
import pytest

from datetime import datetime
import iac_scan_runner.vars as env
from iac_scan_runner.functionality.results_summary import ResultsSummary
from iac_scan_runner.functionality.compatibility import Compatibility


@pytest.fixture
def data_zip_read():
    with open("tests/data/outputs/data_zip", "rb") as f:
        content = f.read()
    return content


@pytest.fixture
def create_mock_UploadFile(mocker):
    def _mock_UploadFile(attr, mockfile=None):
        if mockfile is None:
            mockfile = mocker.MagicMock()

        if "file" in attr:
            mockfile.file = attr["file"]
        if "filename" in attr:
            mockfile.filename = attr["filename"]
        if "content_type" in attr:
            mockfile.content_type = attr["content_type"]
        return mockfile

    return _mock_UploadFile


@pytest.fixture
def create_mock_ScanRunner(mocker):
    def _mock():
        results_summary = ResultsSummary()
        compatibility = Compatibility()

        mock_ScanRunner = mocker.MagicMock()
        mock_ScanRunner.results_summary = results_summary
        mock_ScanRunner.compatibility_matrix = compatibility
        mock_ScanRunner.archive_name = "run_checks_test_data.zip"

        mock_ScanRunner.iac_dir = "run_checks_test_data"

        return mock_ScanRunner

    return _mock


@pytest.fixture
def compatible_checks():
    return [
        "opera-tosca-parser",
        "steampunk-spotter",
        "tflint",
        "tfsec",
        "terrascan",
        "yamllint",
        "pylint",
        "bandit",
        "pyup-safety",
        "git-leaks",
        "git-secrets",
        "markdown-lint",
        "hadolint",
        "gixy",
        "shellcheck",
        "es-lint",
        "ts-lint",
        "htmlhint",
        "stylelint",
        "cloc",
        "checkstyle",
        "snyk",
        "sonar-scanner",
        "ansible-lint",
    ]


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
def htmlhint_response():
    return """\
\n   /home/lukawernig/iac-scan/iac-scan-runner/src/35a0b0/test.html\n\u001b[37m\
      L8 |\u001b[90m</head>\u001b[39m\n\u001b[37m\
          ^ \u001b[31mTag must be paired, no start tag: [ </head> ]\
 (tag-pair)\u001b[39m\n\nScanned 1 files, found 1 errors in 1 files (12 ms)\n"""


@pytest.fixture
def htmlhint_json_response(htmlhint_response):
    return {
        "htmlhint": {
            "log": htmlhint_response,
            "files": "['test.html']",
            "status": "Problems",
        }
    }


# Has logic to either use the existing config file, or if it doesn't exist,
# the saved one below. Not neccessary unless an actual check is in play


@pytest.fixture
def create_mock_check_config(htmlhint_config):
    def _config():
        config_file = list(
            filter(lambda x: x.startswith("mock_check"), os.listdir(env.CONFIG_DIR))
        )
        if config_file:
            with open(f"{env.CONFIG_DIR}/{config_file[0]}", "rb") as f:
                config_content = f.read()
            os.remove(f"{env.CONFIG_DIR}/{config_file[0]}")
            return config_content
        else:
            return htmlhint_config

    return _config


@pytest.fixture
def htmlhint_config():
    return b"""{
  "tagname-lowercase": false,
  "attr-value-double-quotes": false,
  "tag-pair": true,
  "attr-lowercase": false,
  "attr-no-duplication": true,
  "spec-char-escape": true,
  "id-unique": true,
  "src-not-empty": true,
  "title-require": true,
  "attr-value-not-empty": false,
  "doctype-first": false,
  "tag-self-close": false,
  "alt-require": false,
  "doctype-html5": false,
  "style-disabled": false,
  "inline-style-disabled": false,
  "inline-script-disabled": false,
  "space-tab-mixed-disabled": "space",
  "id-class-ad-disabled": false,
  "href-abs-or-rel": false,
  "attr-unsafe-chars": false,
  "head-script-disabled": false
}
"""


@pytest.fixture
def conf_compatibility_matrix():
    return {
        "terraform": [
            "tfsec",
            "tflint",
            "terrascan",
            "git-leaks",
            "git-secrets",
            "cloc",
        ],
        "yaml": [
            "git-leaks",
            "yamllint",
            "git-secrets",
            "ansible-lint",
            "steampunk-spotter",
            "cloc",
            "opera-tosca-parser",
        ],
        "shell": ["shellcheck", "git-leaks", "git-secrets", "cloc"],
        "python": ["pylint", "bandit", "pyup-safety", "cloc"],
        "java": ["checkstyle", "cloc"],
        "js": ["es-lint", "ts-lint", "cloc"],
        "html": ["htmlhint", "cloc"],
        "docker": ["hadolint", "cloc"],
        "common": ["git-leaks", "git-secrets", "cloc"],
        "md": ["markdown-lint", "cloc"],
        "nginx": ["gixy", "cloc"],
        "css": ["stylelint", "cloc"],
        "other": [],
    }


@pytest.fixture
def compatibility_checks():
    return {
        "cloc",
        "ansible-lint",
        "git-secrets",
        "hadolint",
        "bandit",
        "terrascan",
        "htmlhint",
        "steampunk-spotter",
        "shellcheck",
        "checkstyle",
        "pyup-safety",
        "ts-lint",
        "es-lint",
        "opera-tosca-parser",
        "tfsec",
        "git-leaks",
        "pylint",
        "tflint",
        "yamllint",
    }


@pytest.fixture
def compatibility_types():
    return [
        "terraform",
        "yaml",
        "shell",
        "python",
        "java",
        "js",
        "html",
        "docker",
        "common",
        "other",
    ]


@pytest.fixture
def load_project_return():
    def _load(_checklist):
        return {
            "_id": "ObjectId()",
            "project_id": "valid_project_id",
            "creator_id": "creator_id",
            "time": "time",
            "active_config": "",
            "checklist": _checklist,
        }

    return _load


@pytest.fixture
def mock_remove_check():
    def _remove(project_id, check_name):
        if project_id == "valid_project_id":
            with open("mock_DB", "r+") as f:
                project = json.load(f)
                project["checklist"].remove(check_name) if check_name in project[
                    "checklist"
                ] else None
                f.seek(0)
                json.dump(project, f)
                f.truncate()
        else:
            raise Exception("Project id does not exist")

    return _remove


@pytest.fixture
def mock_add_check():
    def _add(project_id, check_name):
        if project_id == "valid_project_id":
            with open("mock_DB", "r+") as f:
                project = json.load(f)
                project["checklist"].append(check_name) if check_name not in project[
                    "checklist"
                ] else None
                f.seek(0)
                json.dump(project, f)
                f.truncate()
        else:
            raise Exception("Project id does not exist")

    return _add


@pytest.fixture
def insert_into_mock_DB():
    def _insert(result):
        with open("mock_DB/entry.json", "w") as f:
            json.dump(result, f)

    return _insert


@pytest.fixture
def insert_into_mock_DB_named():
    def _insert(result, name):
        with open(f"mock_DB/{name}", "w") as f:
            json.dump(result, f)

    return _insert


@pytest.fixture
def load_project_from_mock_DB():
    def _load(query):
        for i in os.listdir("mock_DB"):
            with open(f"mock_DB/{i}") as f:
                content = json.load(f)
                if content["project_id"] == query:
                    return content
                else:
                    break
        raise Exception("Project id does not exist")

    return _load


@pytest.fixture
def select_from_mock_DB():
    def _select(query, ignored=None):
        for i in os.listdir("mock_DB"):
            with open(f"mock_DB/{i}") as f:
                content = json.load(f)
                nonmatching_keys = []
                for k in query.keys():
                    if content[k] != query[k]:
                        nonmatching_keys.append(k)
                        break
                if not nonmatching_keys:
                    return {"content": content, "filename": i}
        return None

    return _select


@pytest.fixture
def update_in_mock_DB(select_from_mock_DB, insert_into_mock_DB_named):
    def _update(query, params, upsert):
        entry = select_from_mock_DB(query)
        if entry:
            parameter_key = [i for i in params["$set"].keys()][0]
            parameter_value = params["$set"][parameter_key]
            entry["content"][parameter_key] = parameter_value
            with open(f"mock_DB/{entry['filename']}", "w") as f:
                json.dump(entry["content"], f)
        elif not entry:
            if upsert:
                content = {**query, **params["$set"]}
                insert_into_mock_DB_named(content, "update.json")

    return _update


@pytest.fixture
def delete_from_mock_DB(select_from_mock_DB):
    def _delete(query):
        entry = select_from_mock_DB(query)
        if entry:
            os.remove(f"mock_DB/{entry['filename']}")

    return _delete


@pytest.fixture
def delete_from_mock_DB_uuid(delete_from_mock_DB):
    def _delete(query):
        query = {"uuid": query}
        delete_from_mock_DB(query)

    return _delete


@pytest.fixture
def find_all():
    def _find(query):
        if query:
            ...
        else:
            output = []
            mock_DB = os.listdir("mock_DB")
            for i in mock_DB:
                with open(f"mock_DB/{i}", "r") as f:
                    content = json.load(f)
                    output.append(content)
        return output

    return _find


@pytest.fixture
def tfsec_output():
    content = """\
\x1b[40mThis is a colored part of the outcome\x1b[0m\nThis was a newline
 Now comes an unicode character "\u001b[J" some space"""
    return content


@pytest.fixture
def tfsec_edited():
    content = """\
 This is a colored part of the outcome  This was a newline  Now comes an unicode character " [J" some space"""
    return content


@pytest.fixture
def is_check():
    def _is_check(check):
        fields = [
            "uuid",
            "time",
            "problems",
            "passed",
            "total",
            "execution-duration",
            "project_id",
            "archive",
        ]
        return bool(check not in fields)

    return _is_check


@pytest.fixture
def results_summary_html_response_passed():
    return


@pytest.fixture
def results_summary_generate_html_outcomes():
    def _outcome(passed):
        if passed:
            outcome = {
                "mock_check_A": {
                    "log": "",
                    "files": "test.html",
                    "status": "Passed",
                },
                "mock_check_B": {
                    "log": "No problems found!",
                    "status": "Passed",
                    "files": "",
                },
                "mock_check_C": {
                    "log": "Information",
                    "status": "Info",
                    "files": "test.js",
                },
                "uuid": "uuid",
                "time": "time",
                "archive": "archive.zip",
                "execution-duration": "0",
                "verdict": "Passed",
                "project_id": "project_id",
            }
        else:
            outcome = {
                "mock_check_A": {
                    "log": "Problems found",
                    "files": "test.html",
                    "status": "Problems",
                },
                "mock_check_B": {
                    "log": "No problems found!",
                    "status": "Passed",
                    "files": "",
                },
                "mock_check_C": {
                    "log": "Information",
                    "status": "Info",
                    "files": "test.js",
                },
                "uuid": "uuid",
                "time": "time",
                "archive": "archive.zip",
                "execution-duration": "0",
                "verdict": "Problems",
                "project_id": "project_id",
            }
        return outcome

    return _outcome


@pytest.fixture
def select_from_mock_DB_checklist(select_from_mock_DB):
    def _select(query, ignored):
        entry = select_from_mock_DB(query)
        if entry:
            return {"checklist": entry["content"]["checklist"]}
        else:
            return None

    return _select


@pytest.fixture
def select_from_mock_DB_content(select_from_mock_DB):
    def _select(query):
        entry = select_from_mock_DB(query)
        if entry:
            return [entry["content"]]
        else:
            return None

    return _select


@pytest.fixture
def load_response():
    def _load_response(response, content_type):
        filename = f"{response}.{content_type}"
        path = os.getcwd() + "/tests/data/outputs/"
        with open(file=(path + filename), mode="r") as f:
            content = f.read()
        return content

    return _load_response


@pytest.fixture
def date_mock():
    def _date(time):
        time1 = datetime.strptime(time, "%m/%d/%Y, %H:%M:%S")
        time2 = datetime.strptime("1/5/1990, 00:00:00", "%m/%d/%Y, %H:%M:%S")
        delta = time2 - time1
        string_delta = str(delta)

        if string_delta.find("days") > -1:
            days = string_delta.split(" ")
            return int(days[0])
        return 0

    return _date


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
