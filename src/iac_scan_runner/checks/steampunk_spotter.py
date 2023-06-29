from typing import Optional

from pydantic import SecretStr
import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class SteampunkSpotterCheck(Check):
    """Steampunk spotter check class object."""

    def __init__(self):
        super().__init__("steampunk-spotter",
                         "provides an Ansible Playbook Scanning Tool that analyzes and offers recommendations"
                         "for your Ansible Playbooks.",
                         CheckTargetEntityType.ALL)
        self.enabled = False
        self.configured = False

        self._config_filename = None

    def configure(self, config_filename: Optional[str],  # pylint: disable=unused-argument
                  secret: Optional[SecretStr]) -> CheckOutput:
        """Set configuration."""
        if secret:
            check_output = run_command(
                f"{env.STEAMPUNK_SPOTTER_CHECK_PATH} --api-token {secret.get_secret_value()} login")
            if not check_output.rc == 0:
                raise Exception(f"Check: {self.name} something went wrong with login. Maybe you used wrong token.")
            if config_filename:
                self._config_filename = config_filename
            return CheckOutput(f"Check: {self.name} has been configured successfully.", 0)
        raise Exception(f"Check: {self.name} requires you to pass user token and an optional configuration file.")

    def run(self, directory: str) -> CheckOutput:
        """Run check."""
        if self._config_filename:
            return run_command(
                f"{env.STEAMPUNK_SPOTTER_CHECK_PATH} scan --config {env.CONFIG_DIR}/{self._config_filename} .",
                directory)
        return run_command(f"{env.STEAMPUNK_SPOTTER_CHECK_PATH} scan .", directory)
