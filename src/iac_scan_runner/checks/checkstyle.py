from os import listdir
from typing import Optional

from pydantic import SecretStr
import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class CheckStyle(Check):
    """Checkstyle check class object."""

    def __init__(self):
        super().__init__("checkstyle", "Checkstyle is a tool for checking Java source code for adherence to a Code "
                                       "Standard or set of validation rules (best practices)",
                         CheckTargetEntityType.IAC)
        self._config_filename = "javalint.xml"

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
            if filename.endswith(".java"):
                check_output = run_command(
                    f"java -jar {env.CHECKSTYLE_CHECK_PATH} -c {env.CONFIG_DIR}/{self._config_filename} {filename}",
                    directory
                )
                output += check_output.output + "\n"
                cnt += check_output.rc
        if not output:
            return CheckOutput("There are no Java files to check.", 0)
        return CheckOutput(output, cnt)
