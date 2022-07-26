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
        return self.outcomes[check_name]

    def set_check_outcome(self, check_name: str, outcome: bool):
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :return: list object conatining string names of checks 
        """
        outcomes[check_name] = outcome

    def summarize_outcome(self, check: str, outcome: str) -> bool:
        """Summarize the check result to True/False depending on the return tool output
        :param check: Name of the considered check of interest
        :return: Whether the check passed (True) or failed (False)
        """

        if check == "tfsec":
            if outcome.find("No problems detected!") > -1:
                self.outcomes[check] = True
                return True
            else:
                self.outcomes[check] = False
                return False

        if check == "git-leaks":
            if outcome.find("No leaks found") > -1:
                self.outcomes[check] = True
                return True
            else:
                self.outcomes[check] = False
                return False

        if check == "tflint":
            if outcome == "":
                self.outcomes[check] = True
                return True
            else:
                self.outcomes[check] = False
                return False

    def show_outcomes(self):
        print(self.outcomes)

    def dump_outcomes(self, file_name: str):
        file_path = "json_dumps/" + file_name + ".json"

        with open(file_path, "w") as fp:
            json.dump(self.outcomes, fp)

    def generate_html(
        self, file_name: str, scanned_files: dict, compatibility_matrix: dict
    ):

        html_page = "<!DOCTYPE html> <html> <style> table, th, td { border:1px solid black;}</style> <body> <h2>Scan results</h2> <table style='width:100%'> <tr> <th>Scan</th><th>Outcome</th><th>Files</th> </tr>"
        # parse scans
        for scan in self.outcomes:

            file_list = ""
            for t in compatibility_matrix:
                if scan in compatibility_matrix[t]:
                    file_list = str(scanned_files[t])

            html_page = html_page + "<tr>"
            html_page = html_page + "<td>" + scan + "</td>"
            html_page = html_page + "<td>" + str(self.outcomes[scan]) + "</td>"
            html_page = html_page + "<td>" + file_list + "</td>"
            html_page = html_page + "</tr>"

        html_page = html_page + "</tr></table></body></html>"

        write_html_to_file(file_name, html_page)
