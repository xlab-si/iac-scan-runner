import os


class Compatibility:
    def __init__(self, matrix: dict):
        """
        Initialize new IaC Compatibility matrix
        :param matrix: dictionary of available checks for given Iac type
        """
        self.compatibility_matrix = matrix
        self.scanned_files = dict()

    def get_check_list(self, iac_type: str) -> list:
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :return: list object conatining string names of checks 
        """
        return self.compatibility_matrix[iac_type]

    def check_iac_type(self, iac_directory: str):
        """Check the type of iac archive
        :param iac_dircetory: Extracted iac archive path"
        :return: Specific type of iac"
        """
        terraform = False
        shell = False
        py = False
        yaml = False
        java = False
        html = False

        types = list()

        scanned_terraform = list()
        scanned_shell = list()
        scanned_py = list()
        scanned_yaml = list()
        scanned_java = list()
        scanned_html = list()

        try:
            for filename in os.listdir(iac_directory):
                f = os.path.join(iac_directory, filename)
                if os.path.isfile(f):
                    if f.find(".tf") > -1:
                        # and (terraform is False):
                        types.append("terraform")
                        terraform = True
                        scanned_terraform.append(filename)

                    if f.find(".sh") > -1:
                        # and (shell is False):
                        types.append("shell")
                        shell = True
                        scanned_shell.append(filename)

                    if f.find(".py") > -1:
                        # and (py is False):
                        types.append("python")
                        py = True
                        scanned_py.append(filename)

                    if f.find(".yaml") > -1:
                        # and (yaml is False):
                        types.append("yaml")
                        yaml = True
                        scanned_yaml.append(filename)

                    if f.find(".java") > -1:
                        # and (yaml is False):
                        types.append("java")
                        java = True
                        scanned_java.append(filename)

                    if f.find(".html") > -1:
                        # and (yaml is False):
                        types.append("html")
                        html = True
                        scanned_html.append(filename)

            self.scanned_files["terraform"] = str(scanned_terraform)
            self.scanned_files["python"] = str(scanned_py)
            self.scanned_files["shell"] = str(scanned_shell)
            self.scanned_files["yaml"] = str(scanned_yaml)
            self.scanned_files["java"] = str(scanned_java)
            self.scanned_files["html"] = str(scanned_html)
            return types
        except Exception as e:
            raise Exception(f"Error when checking directory type: {str(e)}.")

    def get_all_compatible_checks(self, iac_directory: str) -> list:
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :return: list object conatining string names of checks 
        """
        checks_list = list()
        types_list = self.check_iac_type(iac_directory)
        for iac_type in types_list:
            type_checks = self.compatibility_matrix[iac_type]
            for check in type_checks:
                checks_list.append(check)

        print(checks_list)
        return checks_list
