import json
import re
from datetime import datetime
from typing import List, Dict

from iac_scan_runner.utils import write_html_to_file
import iac_scan_runner.vars as env


class ResultsSummary:
    """Scan result summary class object."""

    def __init__(self):
        """
        Initialize new IaC Compatibility matrix.

        :param matrix: dictionary of available checks for given IaC type
        """
        self.outcomes = {}

    def get_check_outcome(self, check_name: str) -> str:
        """
        Return the list of available scanner check tools for given type of IaC archive.

        :return: list object conatining string names of checks
        """
        return self.outcomes[check_name]["status"]

    def set_check_outcome(self, check_name: str, outcome: str) -> None:
        """
        Set the outcome and list of scanned files for specific scanning tool.

        :param check_name: Name of a scan tool
        :param outcome: Scan verdict - passed, failed or no files scanned
        :param file_list: List of files that were scanned using the particular tool
        """
        self.outcomes[check_name] = {}
        self.outcomes[check_name]["status"] = outcome
        self.outcomes[check_name]["files"] = outcome

    def summarize_outcome(self, check: str, outcome: str, scanned_files: Dict["str", List[str]],
                          compatibility_matrix: Dict["str", List[str]]) -> str:
        """
        Summarize the check result to True/False depending on the return tool output.

        :param check: Name of the considered check of interest
        :param outcome: String representing either the check passed, failed or no files were scanned
        :param scanned_files: List of files scanned by particular check tool
        :param compatibility_matrix: Dictionary providing mapping between file types and compatible checks
        :return: Whether the check passed or problems were detected
        """
        self.outcomes[check] = {}
        self.outcomes[check]["log"] = outcome
        file_list = ""
        for item in compatibility_matrix:
            if check in compatibility_matrix[item]:
                file_list = str(scanned_files[item])

        self.outcomes[check]["files"] = file_list

        # TODO: This part should be extended to cover all relevant cases and code refactored
        # TODO: The check names hould not be hardcoded but replaced with parametrized values instead
        # TODO: Extract "Passed" and "Problems" into an Enum object and use them
        if check == "tfsec":
            outcome = re.sub(r"\[[0-9]*m", "", outcome)
            outcome = outcome.replace("\u001b", " ")
            outcome = outcome.replace("\n", " ")

            self.outcomes[check]["log"] = outcome

            if outcome.find("No problems detected!") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "git-leaks":
            if outcome.find("No leaks found") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "git-secrets":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "terrascan":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "tflint":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "htmlhint":
            if outcome.find("no errors") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "checkstyle":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "shellcheck":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "es-lint":
            if outcome.find("wrong") > -1:
                self.outcomes[check]["status"] = "Problems"
                return "Passed"
            self.outcomes[check]["status"] = "Passed"
            return "Problems"

        if check == "ts-lint":
            if outcome.find("wrong") > -1:
                self.outcomes[check]["status"] = "Problems"
                return "Passed"
            self.outcomes[check]["status"] = "Passed"
            return "Problems"

        if check == "pylint":
            if outcome.find("no problems") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "bandit":
            if outcome.find("No issues identified.") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "hadolint":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "terrascan":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "steampunk-spotter":
            outcome = re.sub(r"\x1b+\[\d+m", "", outcome)
            self.outcomes[check]["log"] = outcome
            if outcome.find("SUCCESS") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "cloc":
            self.outcomes[check]["status"] = "Info"
            return "Info"

        if check == "ansible-lint":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        if check == "yamllint":
            if outcome.find("error") > -1:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"
            self.outcomes[check]["status"] = "Passed"
            return "Passed"

        if check == "opera-tosca-parser":
            if outcome.find("Done.") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            self.outcomes[check]["status"] = "Problems"
            return "Problems"

        self.outcomes[check]["status"] = "Not fully supported yet"
        return "Not fully supported yet"

    def summarize_no_files(self, check: str) -> None:
        """
        Set the outcome of the selected check to "no files" case.

        :param check: Name of the considered check of interest
        """
        # TODO: Fields should be extracted into new Python object, probably extending the existing CheckOutput
        self.outcomes[check] = {}
        self.outcomes[check]["status"] = "No files"
        self.outcomes[check]["log"] = ""
        self.outcomes[check]["files"] = ""

    def show_outcomes(self):
        """Print out current summary of the performed checks containing the log and list of scanned files."""
        print(self.outcomes)

    def dump_outcomes(self, file_name: str) -> None:
        """
        Summarize scan results into JSON file.

        :param file_name: Name of the generated JSON file containing the scan summary
        """
        file_path = f"{env.ROOT_DIR}/outputs/json_dumps/" + file_name + ".json"

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.outcomes, file)
        except Exception as e:
            raise Exception(f"Error dumping json of scan results: {str(e)}.") from e

    def is_check(self, check: str) -> bool:
        """Check if iac check."""
        fields = ["uuid", "time", "problems", "passed", "total", "execution-duration", "project_id", "archive"]
        return bool(check not in fields)

    def evaluate_verdict(self) -> str:
        """Set outcome verdict."""
        for check in self.outcomes:
            is_tool = self.is_check(check)
            if is_tool:
                if self.outcomes[check]["status"] == "Problems":
                    self.outcomes["verdict"] = "Problems"
                    return "Problems"
        self.outcomes["verdict"] = "Passed"
        return "Passed"

    def set_result(self, random_uuid, archive_name, duration):
        """Set outcome results."""
        self.outcomes["uuid"] = random_uuid
        self.outcomes["archive"] = archive_name
        self.outcomes["time"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.outcomes["execution-duration"] = str(round(duration, 3))
        self.evaluate_verdict()

    def generate_html_prioritized(self, file_name: str) -> None:
        """
        Summarize scan results.

        :param file_name: Name of the generated HTML file containing the page summary
        """
        with open("src/iac_scan_runner/asset/response.html", "r", encoding="utf-8") as html_template:
            html = html_template.read()

        html = html.replace("CHANGE_ARCHIVE_NAME", self.outcomes["archive"])
        html = html.replace("CHANGE_RUN_START_TIME", self.outcomes["time"])
        html = html.replace("CHANGE_START_TIME", self.outcomes["execution-duration"])
        if self.outcomes["verdict"] == "Problems":
            html = html.replace("CHANGE_FINAL_VERDICT", "Issues found")
        else:
            html = html.replace("CHANGE_FINAL_VERDICT", "No issues found")  # noqa: F841

        table_content = ""
        with open("src/iac_scan_runner/asset/table_problem.html", "r", encoding="utf-8") as html_template:
            html_problem = html_template.read()
        for scan in self.outcomes:
            if scan not in ["uuid", "time", "archive", "execution-duration", "verdict", "project_id"] \
                    and self.outcomes[scan]["status"] == "Problems":
                changeable_html = html_problem
                changeable_html = changeable_html.replace("CHANGE_SCAN", scan)
                changeable_html = changeable_html.replace("CHANGE_STATUS", "Issue")
                changeable_html = changeable_html.replace("CHANGE_FILES", self.outcomes[scan]["files"])
                changeable_html = changeable_html.replace("CHANGE_LOG", self.outcomes[scan]["log"])
                table_content += changeable_html

        with open("src/iac_scan_runner/asset/table_info.html", "r", encoding="utf-8") as html_template:
            html_problem = html_template.read()
        for scan in self.outcomes:
            if scan not in ["uuid", "time", "archive", "execution-duration", "verdict", "project_id"] \
                    and self.outcomes[scan]["status"] == "Info":
                changeable_html = html_problem
                changeable_html = changeable_html.replace("CHANGE_SCAN", scan)
                changeable_html = changeable_html.replace("CHANGE_STATUS", str(self.outcomes[scan]["status"]))
                changeable_html = changeable_html.replace("CHANGE_FILES", self.outcomes[scan]["files"])
                changeable_html = changeable_html.replace("CHANGE_LOG", self.outcomes[scan]["log"])
                table_content += changeable_html

        with open("src/iac_scan_runner/asset/table_passed.html", "r", encoding="utf-8") as html_template:
            html_problem = html_template.read()
        for scan in self.outcomes:
            if scan not in ["uuid", "time", "archive", "execution-duration", "verdict", "project_id"] \
                    and self.outcomes[scan]["status"] in ["Passed"]:
                changeable_html = html_problem
                changeable_html = changeable_html.replace("CHANGE_SCAN", scan)
                changeable_html = changeable_html.replace("CHANGE_STATUS", str(self.outcomes[scan]["status"]))
                changeable_html = changeable_html.replace("CHANGE_FILES", self.outcomes[scan]["files"])
                changeable_html = changeable_html.replace("CHANGE_LOG", self.outcomes[scan]["log"])
                table_content += changeable_html

        with open("src/iac_scan_runner/asset/table_basic.html", "r", encoding="utf-8") as html_template:
            html_problem = html_template.read()
        for scan in self.outcomes:
            if scan not in ["uuid", "time", "archive", "execution-duration", "verdict", "project_id"] \
                    and self.outcomes[scan]["status"] in ["No files"]:
                changeable_html = html_problem
                changeable_html = changeable_html.replace("CHANGE_SCAN", scan)
                changeable_html = changeable_html.replace("CHANGE_STATUS", str(self.outcomes[scan]["status"]))
                changeable_html = changeable_html.replace("CHANGE_FILES", self.outcomes[scan]["files"])
                changeable_html = changeable_html.replace("CHANGE_LOG", self.outcomes[scan]["log"])
                table_content += changeable_html

        html = html.replace("CHANGE_TABLE_CONTENT", table_content)
        write_html_to_file(file_name, html)
