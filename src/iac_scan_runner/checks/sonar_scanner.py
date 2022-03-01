from shutil import copyfile
from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class SonarScannerCheck(Check):
    def __init__(self):
        super().__init__("sonar-scanner", "Official scanner used to run code analysis on SonarQube and SonarCloud",
                         CheckTargetEntityType.all)
        self.enabled = False
        self.configured = False
        self._user_token = None

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            if secret:
                self._user_token = secret
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file and an optional user token.')

    def run(self, directory: str) -> CheckOutput:
        copyfile(f'{env.CONFIG_DIR}/{self._config_filename}', f'{directory}/sonar-project.properties')
        if self._user_token:
            return run_command(f'{env.SONAR_SCANNER_CHECK_PATH} -Dsonar.login={self._user_token.get_secret_value()}',
                               directory)
        else:
            return run_command(f'{env.SONAR_SCANNER_CHECK_PATH}', directory)
