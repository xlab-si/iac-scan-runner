from os import listdir

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class ShellCheck(Check):
    """Shellcheck check class object."""

    def __init__(self):
        super().__init__("shellcheck", "ShellCheck - a static analysis tool for shell scripts",
                         CheckTargetEntityType.IAC)

    def run(self, directory: str) -> CheckOutput:
        """Run check."""
        output = ""
        cnt = 0
        for filename in listdir(directory):
            if filename.endswith(".sh"):
                check_output = run_command(f"{env.SHELL_CHECK_PATH} {filename}", directory)
                output += check_output.output + "\n"
                cnt += check_output.rc
        if not output:
            return CheckOutput("There are no shell scripts to check.", 0)
        return CheckOutput(output, cnt)
