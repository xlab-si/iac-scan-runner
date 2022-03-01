import iac_scan_runner.vars as env
from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class GitSecretsCheck(Check):
    def __init__(self):
        super().__init__("git-secrets", "Prevents you from committing secrets and credentials into git repositories",
                         CheckTargetEntityType.iac)

    def run(self, directory: str) -> CheckOutput:
        return run_command(f'{env.GIT_SECRETS_CHECK_PATH} --scan -r .', directory)
