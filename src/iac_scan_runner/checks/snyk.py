from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class SnykCheck(Check):
    def __init__(self):
        super().__init__("snyk", "Snyk helps you find, fix and monitor known vulnerabilities in open source",
                         CheckTargetEntityType.all)
        self.enabled = False
        self.configured = False

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if secret:
            check_output = run_command(f'snyk auth {secret.get_secret_value()}')
            if check_output.rc == 0:
                return check_output
            else:
                raise Exception(check_output.output)
        else:
            raise Exception(f'Check: {self.name} requires you to pass Snyk API token as secret.')

    def run(self, directory: str) -> CheckOutput:
        return run_command(f'{env.SNYK_CHECK_PATH} test --json', directory)
