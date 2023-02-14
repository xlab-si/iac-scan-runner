from os import listdir

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class PyUpSafetyCheck(Check):
    def __init__(self):
        super().__init__("pyup-safety", "Safety is a PyUp CLI tool that checks your installed Python dependencies for "
                                        "known security vulnerabilities", CheckTargetEntityType.component)

    def run(self, directory: str) -> CheckOutput:
        for filename in listdir(directory):
            if filename == "requirements.txt":
                return run_command(f'{env.SAFETY_CHECK_PATH} check -r requirements.txt', directory)
        return CheckOutput("There is no requirements.txt to check.", 0)
