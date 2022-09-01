import json
from iac_scan_runner.utils import write_html_to_file

class ResultsSummary:
    def __init__(self):
        """
        Initialize new IaC Compatibility matrix
        :param matrix: dictionary of available checks for given IaC type
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
        Sets the outcome and list of scanned files for specific scanning tool
        :param check_name: Name of a scan tool
        :param outcome: Scan verdict - passed, failed or no files scanned
        :param file_list: List of files that were scanned using the particular tool        
        """
        self.outcomes[check_name] = {}
        outcomes[check_name]["status"] = outcome
        outcomes[check_name]["files"] = outcome
                
    def summarize_outcome(
        self, check: str, outcome: str, scanned_files: dict, compatibility_matrix: dict
    ) -> str:
        """Summarize the check result to True/False depending on the return tool output
        :param check: Name of the considered check of interest
        :return: Whether the check passed or problems were detected
        """
        self.outcomes[check] = {}
        self.outcomes[check]["log"] = outcome

        file_list = ""
        for t in compatibility_matrix:
            if check in compatibility_matrix[t]:
                file_list = str(scanned_files[t])

        self.outcomes[check]["files"] = file_list
        
        # TODO: This part should be extended to cover all relevant cases and code refactored
        # TODO: The check names hould not be hardcoded but replaced with parametrized values instead
        # TODO: Extract "Passed" and "Problems" into an Enum object and use them
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

        if check == "htmlhint":
            if outcome.find("no errors")>-1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"

        if check == "checkstyle":
            if outcome == "":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"                

        if check == "es-lint":
            if outcome.find("wrong")>-1:
                self.outcomes[check]["status"] = "Problems"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Passed"
                return "Problems"      

        if check == "ts-lint":
            if outcome.find("wrong")>-1:
                self.outcomes[check]["status"] = "Problems"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Passed"
                return "Problems"  

        if check == "pylint":
            if outcome.find("no problems")>-1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems" 

        if check == "hadolint":
            if outcome=="":
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems" 

        if check == "other":
            self.outcomes[check]["status"] = "No scan performed"
            return "No scan"


    def summarize_no_files(self, check: str):
        """
        Sets the outcome of the selected check to "no files" case
        :param check: Name of the considered check of interest
        """    
        # TODO: Fields should be extracted into new Python object, probably extending the existing CheckOutput
        self.outcomes[check] = {}
        self.outcomes[check]["status"] = "No files"
        self.outcomes[check]["log"] = ""
        self.outcomes[check]["files"] = ""

    def show_outcomes(self):
        """
        Prints out current summary of the performed checks containing the log and list of scanned files
        """        
        print(self.outcomes)

    def dump_outcomes(self, file_name: str):
        """
        Summarizes scan results into JSON file
        :param file_name: Name of the generated JSON file containing the scan summary
        """         
        #TODO: Replace hardcoded path with parameter
        file_path = "../outputs/json_dumps/" + file_name + ".json"

        try:
            with open(file_path, "w") as fp:
                json.dump(self.outcomes, fp)
        except Exception as e:
            raise Exception(f"Error dumping json of scan results: {str(e)}.")


    def generate_html_prioritized(self, file_name: str):
        """
        Summarizes scan results (status, list of scanned files and scan tool log) into HTML file with the following visualization ordering: 1) problems detected 2) passed 3) no files scanned
        :param file_name: Name of the generated HTML file containing the page summary
        """     
        html_page = (
            "<!DOCTYPE html> <html> <style> table, th, td { border:1px solid black;}</style>"
            + "<body> <h2>Scan results</h2>"
            + "<table style='width:100%'>" 
            + "<tr> <th>Scan</th> <th>Status</th> <th>Files</th> <th>Log</th> </tr>"
        )
        
        for scan in self.outcomes:

            if self.outcomes[scan]["status"] == "Problems":

                html_page = html_page + "<tr>"
                html_page = html_page + "<td>" + scan + "</td>"
                html_page = html_page + "<td bgcolor='red'>" + str(self.outcomes[scan]["status"]) + "</td>"

                html_page = html_page + "<td>" + self.outcomes[scan]["files"] + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["log"] + "</td>"
                html_page = html_page + "</tr>"

        for scan in self.outcomes:

            if self.outcomes[scan]["status"] == "Passed":
                html_page = html_page + "<tr>"
                html_page = html_page + "<td>" + scan + "</td>"
                html_page = html_page + "<td bgcolor='green'>" + str(self.outcomes[scan]["status"]) + "</td>"

                html_page = html_page + "<td>" + self.outcomes[scan]["files"] + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["log"] + "</td>"
                html_page = html_page + "</tr>"

        for scan in self.outcomes:

            if self.outcomes[scan]["status"] == "No files":
                html_page = html_page + "<tr>"
                html_page = html_page + "<td>" + scan + "</td>"
                html_page = html_page + "<td bgcolor='gray'>" + str(self.outcomes[scan]["status"]) + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["files"] + "</td>"
                html_page = html_page + "<td>" + self.outcomes[scan]["log"] + "</td>"
                html_page = html_page + "</tr>"

        html_page = html_page + "</tr></table></body></html>"

        write_html_to_file(file_name, html_page)
