from os import listdir
from typing import Optional
from pydantic import SecretStr

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class StyleLintCheck(Check):
    """StyleLint class object."""

    def __init__(self):
        super().__init__("stylelint", "A mighty, modern linter that helps you avoid errors and enforce conventions in "
                                      "your styles", CheckTargetEntityType.IAC)
        self._config_filename = None

    def configure(self, config_filename: Optional[str],
                  secret: Optional[SecretStr]) -> CheckOutput:  # pylint: disable=unused-argument
        """Set configuration."""
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f"Check: {self.name} has been configured successfully.", 0)
        raise Exception(f"Check: {self.name} requires you to pass a configuration file.")

    def run(self, directory: str) -> CheckOutput:
        """Run check."""
        output = ""
        cnt = 0
        for filename in listdir(directory):
            if filename.endswith((".scss", ".sas", ".js", ".css")):
                if self._config_filename:
                    check_output = run_command(
                        f"{env.STYLELINT_CHECK_PATH} --config {env.CONFIG_DIR}/{self._config_filename} "
                        f"--no-error-on-unmatched-pattern --ext .js .", directory
                    )
                else:
                    check_output = run_command(
                        f"{env.STYLELINT_CHECK_PATH} --no-error-on-unmatched-pattern --ext .js .", directory)
                output += check_output.output + "\n"
                cnt += check_output.rc
        if not output:
            return CheckOutput(f"There are no {('.scss', '.sas', '.js', '.css')} scripts to check.", 0)
        return CheckOutput(output, cnt)
