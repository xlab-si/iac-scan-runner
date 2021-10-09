from typing import Optional

import xscanner_runner.vars as env
from pydantic import SecretStr
from xscanner_runner.check import Check
from xscanner_runner.check_output import CheckOutput
from xscanner_runner.check_target_entity_type import CheckTargetEntityType
from xscanner_runner.utils import run_command


class TerrascanCheck(Check):
    def __init__(self):
        super().__init__("terrascan", "Terrascan is a static code analyzer for IaC (defaults to scanning Terraform)",
                         CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        if self._config_filename:
            return run_command(f'{env.TERRASCAN_PATH} -c {env.CONFIG_DIR}/{self._config_filename} scan', directory)
        else:
            return run_command(f'{env.TERRASCAN_PATH} scan', directory)
