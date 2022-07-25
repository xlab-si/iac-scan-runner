import os
import json


from iac_scan_runner.utils import write_html_to_file


class ResultsSummary:
    def __init__(self):
        """
        Initialize new IaC Compatibility matrix
        :param matrix: dictionary of available checks for given Iac type
        """
        self.outcomes = dict()

    def get_check_outcome(self, check_name: str) -> str:
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :return: list object conatining string names of checks 
        """
        return self.outcomes[check_name]["status"]

    def set_check_outcome(self, check_name: str, outcome: str, file_list: str):
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :return: list object conatining string names of checks 
        """
        self.outcomes[check] = {}
        outcomes[check_name]["status"] = outcome

    def summarize_outcome(
        self, check: str, outcome: str, scanned_files: dict, compatibility_matrix: dict
    ) -> str:
        """Summarize the check result to True/False depending on the return tool output
        :param check: Name of the considered check of interest
        :return: Whether the check passed (True) or failed (False)
        """
        self.outcomes[check] = {}
        self.outcomes[check]["log"] = outcome

        file_list = ""
        for t in compatibility_matrix:
            if check in compatibility_matrix[t]:
                file_list = str(scanned_files[t])

        self.outcomes[check]["files"] = file_list

        if check == "tfsec":
            if outcome.find("No problems detected!") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"

        if check == "git-leaks":
            if outcome.find("No leaks found") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"

        if check == "tflint":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"

    def summarize_no_files(self, check: str):
        self.outcomes[check] = {}
        self.outcomes[check]["status"] = "No files"
        self.outcomes[check]["log"] = ""
        self.outcomes[check]["files"] = ""

    def show_outcomes(self):
        print(self.outcomes)

    def dump_outcomes(self, file_name: str):
        file_path = "../outputs/json_dumps/" + file_name + ".json"

        with open(file_path, "w") as fp:
            json.dump(self.outcomes, fp)

    def generate_html_prioritized(self, file_name: str):
        html_page = "<!DOCTYPE html> <html> <style> table, th, td { border:1px solid black;}</style> <body> <h2>Scan results</h2> <table style='width:100%'> <tr> <th>Scan</th><th>Status</th><th>Files</th><th>Log</th> </tr>"
        # parse scans
        for scan in self.outcomes:

            if self.outcomes[scan]["status"] == "Problems":

                html_page = html_page + "<tr>"
                html_page = html_page + "<td>" + scan + "</td>"
                html_page = (
                    html_page
                    + "<td bgcolor='red'>"
                    + str(self.outcomes[scan]["status"])
                    + "</td>"
                )

                html_page = html_page + "<td>" + self.outcomes[scan]["files"] + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["log"] + "</td>"
                html_page = html_page + "</tr>"

        for scan in self.outcomes:

            if self.outcomes[scan]["status"] == "Passed":
                html_page = html_page + "<tr>"
                html_page = html_page + "<td>" + scan + "</td>"
                html_page = (
                    html_page
                    + "<td bgcolor='green'>"
                    + str(self.outcomes[scan]["status"])
                    + "</td>"
                )

                html_page = html_page + "<td>" + self.outcomes[scan]["files"] + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["log"] + "</td>"
                html_page = html_page + "</tr>"

        for scan in self.outcomes:

            if self.outcomes[scan]["status"] == "No files":
                html_page = html_page + "<tr>"
                html_page = html_page + "<td>" + scan + "</td>"
                html_page = (
                    html_page
                    + "<td bgcolor='gray'>"
                    + str(self.outcomes[scan]["status"])
                    + "</td>"
                )
                html_page = html_page + "<td>" + self.outcomes[scan]["files"] + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["log"] + "</td>"
                html_page = html_page + "</tr>"

        html_page = html_page + "</tr></table></body></html>"

        write_html_to_file(file_name, html_page)
