class CheckOutput:
    def __init__(self, output: str, rc: int):
        """Initialize new IaC check output

         :param output: Returned check output
         :param rc: Check return code
        """
        self.output = output
        self.rc = rc

    def to_dict(self) -> dict:
        """Transform CheckOutput object to dict"""
        return {"output": self.output, "rc": self.rc}
