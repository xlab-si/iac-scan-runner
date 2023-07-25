from typing import Optional

from pydantic import SecretStr
import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class SnykCheck(Check):
    """Snyk class object."""

    def __init__(self):
        super().__init__("snyk", "Snyk helps you find, fix and monitor known vulnerabilities in open source",
                         CheckTargetEntityType.ALL)
        self.enabled = False
        self.configured = False

    def configure(self, config_filename: Optional[str],  # pylint: disable=unused-argument
                  secret: Optional[SecretStr]) -> CheckOutput:  # pylint: disable=unused-argument
        """Set configuration."""
        if secret:
            check_output = run_command(f"{env.SNYK_CHECK_PATH} auth {secret.get_secret_value()}")
            if check_output.rc == 0:
                return check_output
            raise Exception(check_output.output)
        raise Exception(f"Check: {self.name} requires you to pass Snyk API token as secret.")

    def run(self, directory: str) -> CheckOutput:
        """Run check."""
        return run_command(f"{env.SNYK_CHECK_PATH} test --json", directory)
