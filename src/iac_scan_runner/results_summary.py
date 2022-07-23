import os
import json


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
