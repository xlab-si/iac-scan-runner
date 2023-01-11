from os import listdir
from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class GixyCheck(Check):
    def __init__(self):
        super().__init__("gixy", "Gixy is a tool to analyze Nginx configuration", CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        for filename in listdir(directory):
            if filename == "nginx.conf":
                if self._config_filename:
                    return run_command(f'{env.GIXY_CHECK_PATH} -c {env.CONFIG_DIR}/{self._config_filename} {filename}',
                                       directory)
                else:
                    return run_command(f'{env.GIXY_CHECK_PATH} {filename}', directory)
        return CheckOutput("There is no nginx.conf file to check.", 0)
