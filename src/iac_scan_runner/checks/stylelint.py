from os import listdir
from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class StyleLintCheck(Check):
    def __init__(self):
        super().__init__("stylelint", "A mighty, modern linter that helps you avoid errors and enforce conventions in "
                                      "your styles", CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        output = ""
        rc = 0
        for filename in listdir(directory):
            if filename.endswith((".scss", ".sas", ".js", ".css")):
                if self._config_filename:
                    check_output = run_command(
                        f'{env.STYLELINT_CHECK_PATH} --config {env.CONFIG_DIR}/{self._config_filename} '
                        f'--no-error-on-unmatched-pattern --ext .js .', directory
                    )
                else:
                    check_output = run_command(
                        f'{env.STYLELINT_CHECK_PATH} --no-error-on-unmatched-pattern --ext .js .', directory)
                output += check_output.output + "\n"
                rc += check_output.rc
        if not output:
            return CheckOutput(f'There are no {(".scss", ".sas", ".js", ".css")} scripts to check.', 0)
        return CheckOutput(output, rc)
