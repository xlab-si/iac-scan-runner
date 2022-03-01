from os import listdir
from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class HadolintCheck(Check):
    def __init__(self):
        super().__init__("hadolint", "Dockerfile linter, validate inline bash, written in Haskell",
                         CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        for filename in listdir(directory):
            if filename == "Dockerfile":
                if self._config_filename:
                    return run_command(
                        f'{env.HADOLINT_CHECK_PATH} -c {env.CONFIG_DIR}/{self._config_filename} Dockerfile',
                        directory)
                else:
                    return run_command(f'{env.HADOLINT_CHECK_PATH} Dockerfile', directory)
        return CheckOutput("There is no Dockerfile to check.", 0)
