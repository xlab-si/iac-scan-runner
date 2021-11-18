from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class GitLeaksCheck(Check):
    def __init__(self):
        super().__init__("git-leaks", "Gitleaks is a SAST tool for detecting hardcoded secrets like passwords, API "
                                      "keys, and tokens in Git repos", CheckTargetEntityType.iac)

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        if self._config_filename:
            return run_command(
                f'{env.GIT_LEAKS_PATH} --config-path {env.CONFIG_DIR}/{self._config_filename} --path=. -v', directory
            )
        else:
            return run_command(f'{env.GIT_LEAKS_PATH} --path=. -v', directory)
