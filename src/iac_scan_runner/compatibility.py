import os
from typing import List


class Compatibility:
    # TODO: This matrix should be revised and extended, it is just a proof of concept here as for now
    compatibility_matrix = {
        "terraform": ["tfsec", "tflint", "terrascan", "git-leaks", "git-secrets", "cloc"],
        "yaml": ["git-leaks", "yamllint", "git-secrets", "ansible-lint", "steampunk-scanner", "cloc"],
        "shell": ["shellcheck", "git-leaks", "git-secrets", "cloc"],
        "python": ["pylint", "bandit", "pyup-safety", "cloc"],
        "java": ["checkstyle", "cloc"],
        "js": ["es-lint", "ts-lint", "cloc"],
        "html": ["htmlhint", "cloc"],
        "docker": ["hadolint", "cloc"],
        "common": ["git-leaks", "git-secrets", "cloc"],
        "other": []
    }

    def __init__(self):
        """
        Initialize new IaC Compatibility matrix
        """
        self.scanned_files = dict()

    def get_check_list(self, iac_type: str) -> List[str]:
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :iac_type: Type of IaC file for which we consider the list of compatible scans        
        :return: List with names of checks as strings 
        """
        return self.compatibility_matrix[iac_type]

    def check_iac_type(self, iac_directory: str) -> List[str]:
        """Check the type of IaC archive
        :param iac_directory: Extracted IaC archive path
        :return: List of specific file types within the given IaC directory
        """

        types = []

        scanned_terraform = []
        scanned_shell = []
        scanned_py = []
        scanned_yaml = []
        scanned_java = []
        scanned_html = []
        scanned_js = []
        scanned_docker = []
        scanned_other = []
        scanned_all = []
        # TODO: List of supported file types should be extended
        # TODO: Remove hardcoded check names
        try:
            for root, folders, names in os.walk(iac_directory):
                for f in names:
                    scanned_all.append(f)
                    if (f.find(".tf") > -1) or (f.find(".tftpl") > -1):
                        types.append("terraform")
                        scanned_terraform.append(f)

                    elif (f.find(".yaml") > -1) or (f.find(".yml") > -1):
                        types.append("yaml")
                        scanned_yaml.append(f)

                    elif f.find(".sh") > -1:
                        types.append("shell")
                        scanned_shell.append(f)

                    elif f.find(".py") > -1:
                        types.append("python")
                        scanned_py.append(f)

                    elif f.find(".java") > -1:
                        types.append("java")
                        scanned_java.append(f)

                    elif f.find(".html") > -1:
                        types.append("html")
                        scanned_html.append(f)

                    elif f.find(".js") > -1:
                        types.append("js")
                        scanned_js.append(f)

                    elif f.find("Dockerfile") > -1:
                        types.append("docker")
                        scanned_docker.append(f)

                    else:
                        types.append("other")
                        scanned_other.append(f)

            types.append("common")

            self.scanned_files["terraform"] = str(scanned_terraform)
            self.scanned_files["python"] = str(scanned_py)
            self.scanned_files["shell"] = str(scanned_shell)
            self.scanned_files["yaml"] = str(scanned_yaml)
            self.scanned_files["java"] = str(scanned_java)
            self.scanned_files["html"] = str(scanned_html)
            self.scanned_files["js"] = str(scanned_js)
            self.scanned_files["docker"] = str(scanned_docker)
            self.scanned_files["other"] = str(scanned_other)
            self.scanned_files["common"] = str(scanned_all)

            types = list(dict.fromkeys(types))

            return types
        except Exception as e:
            raise Exception(f"Error when checking directory type: {str(e)}.")

    def get_all_compatible_checks(self, iac_directory: str) -> List[str]:
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :param iac_directory: Extracted IaC archive path
        :return: List with names of compatible checks as strings 
        """
        checks_list = []
        types_list = self.check_iac_type(iac_directory)
        for iac_type in types_list:
            type_checks = self.compatibility_matrix[iac_type]
            for check in type_checks:
                checks_list.append(check)

        return checks_list
