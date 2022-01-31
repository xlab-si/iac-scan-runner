from iac_scan_runner.check import Check
from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class OperaToscaCheck(Check):
    def __init__(self):
        super().__init__("xopera", "A TOSCA orchestrator that can validate TOSCA CSARs", CheckTargetEntityType.iac)

    def run(self, directory: str) -> CheckOutput:
        return run_command(f'opera validate .', directory)
