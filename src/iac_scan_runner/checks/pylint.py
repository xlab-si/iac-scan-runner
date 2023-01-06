from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enum.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class PylintCheck(Check):
    def __init__(self):
        super().__init__("pylint", "Pylint is a Python static code analysis tool that checks for errors in Python "
                                   "code, tries to enforce a coding standard and looks for code smells",
                         CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        if self._config_filename:
            return run_command(f'{env.PYLINT_CHECK_PATH} --rcfile {env.CONFIG_DIR}/{self._config_filename} .',
                               directory)
        else:
            return run_command(f'{env.PYLINT_CHECK_PATH} .', directory)
