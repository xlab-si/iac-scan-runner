class Compatibility:
    def __init__(self, matrix: dict):
        """
        Initialize new IaC Compatibility matrix
        :param matrix: dictionary of available checks for given Iac type
        """
        self.compatibility_matrix = matrix

    def get_check_list(self, iac_type: str) -> list:
        """
        Returns the list of available scanner check tools for given type of IaC archive
        :return: list object conatining string names of checks 
        """
        return self.compatibility_matrix[iac_type]
