from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command
from pydantic import SecretStr


class AnsibleLintCheck(Check):
    def __init__(self):
        super().__init__("ansible-lint", "Ansible Lint is a command-line tool for linting playbooks, roles and "
                                         "collections aimed towards any Ansible users", CheckTargetEntityType.iac)
        self.counter = 0

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]) -> CheckOutput:
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f'Check: {self.name} has been configured successfully.', 0)
        else:
            raise Exception(f'Check: {self.name} requires you to pass a configuration file.')

    def run(self, directory: str) -> CheckOutput:
        if self._config_filename:
            return run_command(f'{env.ANSIBLE_LINT_CHECK_PATH} -p -c {env.CONFIG_DIR}/{self._config_filename}',
                               directory)
        else:
            return run_command(f'{env.ANSIBLE_LINT_CHECK_PATH} -p', directory)
