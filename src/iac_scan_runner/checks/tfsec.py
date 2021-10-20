from typing import Optional

import src.iac_scan_runner.vars as env
from pydantic import SecretStr
from src.iac_scan_runner.check import Check
from src.iac_scan_runner.check_output import CheckOutput
from src.iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from src.iac_scan_runner.utils import run_command


class TfsecCheck(Check):
    def __init__(self):
        super().__init__("tfsec", "Security scanner for your Terraform code", CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        if self._config_filename:
            return run_command(f'{env.TF_SEC_PATH} --config-file {env.CONFIG_DIR}/{self._config_filename} .', directory)
        else:
            return run_command(f'{env.TF_SEC_PATH} .', directory)
