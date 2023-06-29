import os
from typing import Optional

from pydantic import SecretStr
import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class SteampunkScannerCheck(Check):
    """Steampunk Spotter check class object."""

    def __init__(self):
        super().__init__("steampunk-scanner", "A quality scanner for Ansible tasks, playbooks, roles and collections",
                         CheckTargetEntityType.ALL)
        self.enabled = False
        self.configured = False
        self._username_password = None

    def configure(self, config_filename: Optional[str],  # pylint: disable=unused-argument
                  secret: Optional[SecretStr]) -> CheckOutput:
        """Set configuration."""
        if secret:
            try:
                if ":" not in secret.get_secret_value():
                    raise Exception(
                        f'The secret for {self.name} check should contain ":" to separate username and password.'
                    )

                os.environ["SCANNER_USERNAME"], os.environ[
                    "SCANNER_PASSWORD"] = secret.get_secret_value().strip().split(":", 1)
                return CheckOutput(f"Check: {self.name} has been configured successfully.", 0)
            except Exception as e:
                raise Exception(f"Error when configuring {self.name}. Check your username:password secret.") from e
        raise Exception(f"Check: {self.name} requires you to pass username:password string as secret.")

    def run(self, directory: str) -> CheckOutput:
        """Run check."""
        return run_command(f"{env.STEAMPUNK_SCANNER_CHECK_PATH} scan .", directory)
