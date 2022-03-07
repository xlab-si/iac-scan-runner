class CheckOutput:
    def __init__(self, output: str, rc: int):
        """
        Initialize new IaC check output
        :param output: Returned check output
        :param rc: Check return code
        """
        self.output = output
        self.rc = rc

    def to_dict(self) -> dict:
        """
        Transform CheckOutput object to dict (for JSON response)
        :return: dict with check output and return code
        """
        return {"output": self.output, "rc": self.rc}

    def to_string(self) -> str:
        """
        Transform CheckOutput object to string (for HTML response)
        :return: string with result for check output
        """
        return f'Return code: {self.rc}\nOutput: {self.output}'
